#!/usr/bin/env python3

import re
import html_string_tools
import python_print_tools
import gallery_dvk.extractor.extractor
from typing import List

class DocsLab(gallery_dvk.extractor.extractor.Extractor):
    def __init__(self, config_paths:List[str]=gallery_dvk.config.get_default_config_paths()):
        """
        Creates the DocsLab object and loads configuration files.
        
        :param config_paths: Paths to attempt to read as a configuration file, defaults to default config paths
        :type config_paths: list[str]
        """
        super().__init__(category="docslab", config_paths=config_paths)
        # Set the URL matchers
        self.url_matchers = []
        user_match = r"(?:https?:\/\/)?(?:www\.)?docs-lab.com\/profiles\/[^\/]+\/?$"
        user_section = r"(?<=docs-lab.com\/profiles\/)[^\/]+(?=\/?$)"
        self.url_matchers.append({"match":user_match, "section":user_section, "type":"user"})
        sub_match = r"(?:https?:\/\/)?(?:www\.)?docs-lab.com\/submissions\/[0-9]+\/[^\/]+\/?$"
        self.sub_section = r"(?<=docs-lab.com\/submissions\/)[0-9]+\/[^\/]+(?=\/?$)"
        self.url_matchers.append({"match":sub_match, "section":self.sub_section, "type":"submission"})
        # Set the default include values if necessary
        if self.include == []:
            self.include = ["submissions"]
        # Set the default filename format, if necessary
        if self.filename_format == "{title}":
            self.filename_format = "{id}_{title}"

    def download_submission(self, section:str, directory:str) -> bool:
        """
        Attempt to download a DocsLab submission.
        
        :param section: Section of URL used to get submission, should contain submission ID
        :type section: str, required
        :param directory: Directory to save files into
        :type directory: str, required
        :return: Whether download was successful
        :rtype: bool
        """
        try:
            page = self.get_submission_info(section)
            assert page is not None
            self.download_page(page, directory)
            return True
        except AssertionError:
            python_print_tools.color_print(f"Failed to download: {section}", "red")
            return False

    def download_user(self, section:str, directory:str) -> bool:
        """
        Attempt to download Doc's Lab submission from a given user.
        
        :param section: Section of URL used to get the submissions, should be Doc's Lab username
        :type section: str, required
        :param directory: Directory to save files into
        :type directory: str, required
        :return: Whether download was successful
        :rtype: bool
        """
        subs = "submissions" in self.include
        favs = "favorites" in self.include
        submissions = self.get_links_from_user(section, get_submissions=subs, get_favorites=favs)
        for submission in submissions:
            try:
                page = self.get_submission_info(submission["section"], submission["rating"])
                assert page is not None
                self.download_page(page, directory)
            except AssertionError:
                python_print_tools.color_print(f"Failed to download: {submission['section']}", "red")
                return False
        return True

    def get_info_from_config(self, config:dict, category:str):
        """
        Sets variables in the Extractor object based on values in a given config dictionary.
        
        :param config: Dictionary containing gallery-dvk config info
        :type config: dict, required
        :param category: Category of extractor to search config file for
        :type category: str, required
        """
        super().get_info_from_config(config, "docslab")
        # Get whether to download linked stories
        self.download_stories = gallery_dvk.extractor.extractor.get_category_value(config, category, "download_stories", [bool], False)
        # Get whether to download linked artwork
        self.download_artwork = gallery_dvk.extractor.extractor.get_category_value(config, category, "download_artwork", [bool], False)

    def get_id(self, url:str) -> str:
        """
        Gets the id for a Doc's Lab page.

        :param url: Doc's Lab submission URL
        :type url: str, required
        :return: ID for the submission URL
        :rtype: str
        """
        section = re.findall(r"(?<=docs-lab.com\/submissions\/)[0-9]+(?=\/)", url)[0]
        return f"docslab-{section}"

    def get_links_from_user(self, user:str, get_submissions:bool, get_favorites:bool) -> List[dict]:
        """
        Returns a list of submission links from a given user.
        Can be a list of the users own submissions, favorited submissions, or both.
        Each entry is a dict containing the submission section and the submission age rating.

        :param user: Username of the Doc's Lab user profile to scan
        :type user: str, required
        :param get_submissions: Whether to get the submissions from the user profile
        :type get_submissions: bool, required
        :param get_favorites: Whether to get the favorited submissions from the user profile
        :type get_favorites: bool, required
        :return: List of links with their corresponding age ratings
        :rtype: list[dir]
        """
        # Load page
        bs = self.web_get(f"https://www.docs-lab.com/profiles/{user}")
        # Get submissions
        submissions = []
        sub_container = bs.find("div", {"id":"submissions"})
        sub_elements = sub_container.find_all("tr", {"data-href":re.compile(r"submissions\/[0-9]+")})
        for sub_element in sub_elements:
            section = re.findall(self.sub_section, "docs-lab.com" + sub_element["data-href"])[0]
            rating_element = sub_element.find("td", {"class":"text-center"}, string=re.compile(r"^\s*[RXP]G?\s*$"))
            rating = rating_element.get_text().strip()
            submissions.append({"section":section, "rating":rating})
        # Get favorites
        favorites = []
        fav_container = bs.find("div", {"id":"tab-favorites"})
        fav_elements = fav_container.find_all("a", {"href":re.compile(r"submissions\/[0-9]+")})
        for fav_element in fav_elements:
            section = re.findall(self.sub_section, "docs-lab.com" + fav_element["href"])[0]
            favorites.append({"section":section, "rating":None})
        # Combine links as needed
        links = []
        if get_submissions:
            links.extend(submissions)
        if get_favorites:
            links.extend(favorites)
        # Remove already downloaded links
        for i in range(len(links)-1, -1, -1):
            href = "docs-lab.com/submissions/" + links[i]["section"]
            if self.archive_contains(self.get_id(href)):
                del links[i]
        # Return links
        return links
    
    def get_submission_info(self, section:str, age_rating:str=None) -> dict:
        """
        Returns a dictionary containing info from a given Doc's Lab submission.
        Submission can be either a story or an art piece.

        :param section: Section of Doc's Lab submission URL identifying the submission
        :type section: str, required
        :param age_rating: Age rating of the submission, searches for rating if None, defaults to None
        :type age_rating: str, optional
        :return: Dictionary containing info of the submission
        :rtype: dictionary
        """
        # Get the submission URL and ID
        submission = {"id":re.findall("^[0-9]+", section)[0]}
        submission["url"] = f"https://www.docs-lab.com/submissions/{section}"
        # Load the submission page
        bs = self.web_get(submission["url"])
        # Get the title
        try:
            title = bs.find("h2", {"style":re.compile("[A-Za-z]+")}).get_text()
            submission["title"] = title.strip()
        except AttributeError:
            return None
        # Get the artist
        artist_element = bs.find("a", {"href":re.compile(r"profiles\/")}).find("strong")
        artist = artist_element.get_text()
        submission["artist"] = artist.strip()
        # Get the date
        date_containers = bs.find_all("div", {"class":re.compile(r"col-xs")})
        for date_container in date_containers:
            if len(re.findall("[Pp]ublished:", date_container.get_text())) > 0:
                date_string = re.findall(r"(?<=ublished:)[^:]+", date_container.get_text())[0]
                submission["date"] = gallery_dvk.extractor.extractor.get_date(date_string)
                try:
                    date_string = re.findall(r"(?<=dit:)[^:]+", date_container.get_text())[0]
                    submission["last_edit"] = gallery_dvk.extractor.extractor.get_date(date_string)
                except IndexError: submission["last_edit"] = submission["date"]
                break
        # Get the tags
        tags = []
        tag_elements = bs.find_all("span", {"class":"label", "data-submission-id":re.compile("[0-9]+")})
        for tag_element in tag_elements:
            tags.append(re.sub(r"^\s+|\s*\([0-9]+\)\s*$", "", tag_element.get_text()))
        submission["tags"] = tags
        # Get the age rating
        submission["age_rating"] = age_rating
        if submission["age_rating"] is None:
            links = self.get_links_from_user(submission["artist"], get_submissions=True, get_favorites=False)
            for link in links:
                if link["section"] == section:
                    submission["age_rating"] = link["rating"]
                    break
        # Get the user rating
        try:
            rating_element = bs.find("span", {"class":"headline"}, string=re.compile(r"[Uu]ser\s+[Rr]ating"))
            user_rating = rating_element.parent.find("span", {"class":"value"}).get_text()
            submission["user_rating"] = int(user_rating.strip())
        except ValueError: submission["user_rating"] = 0
        # Get the number of favorites
        try:
            favorites_element = bs.find("span", {"class":"headline"}, string=re.compile(r"[Ff]avorites?"))
            favorites = favorites_element.parent.find("span", {"class":"value"}).get_text()
            submission["favorites"] = int(favorites.strip())
        except ValueError: submission["favorites"] = 0
        # Get the description
        try:
            description = bs.find("h3", string=re.compile("[Dd]escription")).parent.get_text()
            description = re.sub(r"^\s*[Dd]escription\s+|\s+$", "", description)
            description = description.replace("\r", "\n").replace("\n", "<br/>")
            description = re.sub(r"\s*<br\/>\s*", "<br/>", description)
            description = re.sub(r"(<br\/>){3,}", "<br/><br/>", description)
            submission["description"] = description
        except AttributeError: submission["description"] = None
        # Get the story, if available
        submission["text"] = None
        story_header = bs.find("h2", string=re.compile(r"^\s*[Ss]tory"))
        if story_header is not None:
            for parent in story_header.parents:
                try:
                    story_element = parent.find("div", {"class":"main-box-body"})
                    paragraphs = story_element.find_all("p")
                    text = "<!DOCTYPE html><html><body>"
                    for paragraph in paragraphs:
                        paragraph_text = str(paragraph)
                        paragraph_text = re.sub(r"^\s*<p>\s+", "<p>", paragraph_text)
                        paragraph_text = re.sub(r"\s+<\/p>\s*$", "</p>", paragraph_text)
                        paragraph_text = paragraph_text.replace("<p></p>", "")
                        text = f"{text}{paragraph_text}"
                    text = f"{text}</body></html>"
                    submission["text"] = text
                    break
                except AttributeError: pass
        # Get the image, if available
        submission["image_url"] = None
        image_header = bs.find("h2", string=re.compile(r"[Ii]mage"))
        if image_header is not None:
            for parent in image_header.parents:
                try:
                    image_element = parent.find("img", {"src":re.compile(r"\/img\/art\/")})
                    submission["image_url"] = "https://www.docs-lab.com" + image_element["src"]
                    break
                except (AttributeError, TypeError): pass
        # Get the story submission link, if available
        submission["story_link"] = None
        story_header = bs.find("h2", string=re.compile(r"[Pp]arent\s+[Ss]tory"))
        if story_header is not None:
            for parent in story_header.parents:
                try:
                    sub_link = parent.find("a", {"href":re.compile(r"\/submissions\/[0-9]+")})
                    submission["story_link"] = "https://www.docs-lab.com" + sub_link["href"]
                    break
                except (AttributeError, TypeError): pass
        # Get the art submission link, if available
        try:
            thumbnail_container = bs.find("a", {"class":"art-thumbnail-container"})
            submission["art_link"] = "https://www.docs-lab.com" + thumbnail_container["href"]
        except TypeError: submission["art_link"] = None
        # Set the submission type
        submission["type"] = "story"
        if submission["text"] is None:
            submission["type"] = "art"
        # Return the submission dictionary
        return submission

    def download_page(self, page:dict, directory:str) -> str:
        """
        Downloads a given Doc's Lab submission page.
    
        :param page: Metadata dict for a given Doc's Lab submission page.
        :type page: dict, required
        :param directory: Directory to save files into
        :type directory: str, required
        :return: Path of the media file created, if applicable
        :rtype: str
        """
        # Download the main page
        subs = ["DocsLab", page["artist"]]
        main_media = super().download_page(page, directory, subs)
        # Download linked images
        if page["art_link"] is not None and self.download_artwork:
            section = re.findall(self.sub_section, page["art_link"])[0]
            art_page = self.get_submission_info(section)
            subs = ["DocsLab", art_page["artist"]]
            art_media = super().download_page(art_page, directory, subs)
        # Download linked stories
        if page["story_link"] is not None and self.download_stories:
            section = re.findall(self.sub_section, page["story_link"])[0]
            story_page = self.get_submission_info(section)
            subs = ["DocsLab", story_page["artist"]]
            story_media = super().download_page(story_page, directory, subs) 
        return main_media
