#!/usr/bin/env python3

import re
import gallery_dvk.extractor.extractor
from typing import List

class Transfur(gallery_dvk.extractor.extractor.Extractor):
    def __init__(self, config_paths:List[str]=gallery_dvk.config.get_default_config_paths()):
        """
        Creates the Transfur object and loads configuration files.
        
        :param config_paths: Paths to attempt to read as a configuration file, defaults to default config paths
        :type config_paths: list[str]
        """
        super().__init__(category="transfur", config_paths=config_paths)
        # Set the URL matchers
        self.url_matchers = []
        user_match = r"(?:https?:\/\/)?(?:www\.)?transfur\.com\/users\/[^\/]+\/?$"
        user_section = r"(?<=transfur.com\/users\/)[^\/]+(?=\/?$)"
        self.url_matchers.append({"match":user_match, "section":user_section, "type":"user"})
        gallery_match = r"(?:https?:\/\/)?(?:www\.)?transfur\.com\/users\/[^\/]+\/gallery\/?[^\/]*\/?$"
        gallery_section = r"(?<=transfur\.com\/users\/)[^\/]+(?=\/gallery)"
        self.url_matchers.append({"match":gallery_match, "section":gallery_section, "type":"gallery"})
        sketch_match = r"(?:https?:\/\/)?(?:www\.)?transfur\.com\/users\/[^\/]+\/sketches\/?[^\/]*\/?$"
        sketch_section = r"(?<=transfur\.com\/users\/)[^\/]+(?=\/sketches)"
        self.url_matchers.append({"match":sketch_match, "section":sketch_section, "type":"sketches"})
        favorites_match = r"(?:https?:\/\/)?(?:www\.)?transfur\.com\/users\/[^\/]+\/favorites\/?[^\/]*\/?$"
        favorites_section = r"(?<=transfur\.com\/users\/)[^\/]+(?=\/favorites)"
        self.url_matchers.append({"match":favorites_match, "section":favorites_section, "type":"favorites"})
        tag_match = r"(?:https?:\/\/)?(?:www\.)?transfur\.com\/tags\/[^\/]+\/?[^\/]*\/?$"
        tag_section = r"(?<=transfur\.com\/tags\/)[^\/]+(?=\/?[^\/]*\/?$)"
        self.url_matchers.append({"match":tag_match, "section":tag_section, "type":"tag"})
        sub_match = r"(?:https?:\/\/)?(?:www\.)?transfur\.com\/users\/[^\/]+\/submissions\/[0-9]+\/?[^\/]*\/?$"
        self.sub_section = r"(?<=transfur.com\/users\/)[^\/]+\/submissions\/[0-9]+"
        self.url_matchers.append({"match":sub_match, "section":self.sub_section, "type":"submission"})
        # Set the default include values if necessary
        if self.include == []:
            self.include = ["gallery", "sketches"]
        # Set the default filename format, if necessary
        if self.filename_format == "{title}":
            self.filename_format = "{id}_{title}"
    
    def download_submission(self, section:str, directory:str) -> bool:
        """
        Attempt to download a Transfur submission.
        
        :param section: Section of URL used to get submission, should contain submission ID
        :type section: str, required
        :param directory: Directory to save files into
        :type directory: str, required
        :return: Whether download was successful
        :rtype: bool
        """
        pages = self.get_info_from_page(section)
        for page in pages:
            self.download_page(page, directory)
        return True
    
    def download_gallery(self, section:str, directory:str) -> bool:
        """
        Attempt to download a Transfur gallery.
        
        :param section: Section of URL used to get the gallery, should be Transfur username
        :type section: str, required
        :param directory: Directory to save files into
        :type directory: str, required
        :return: Whether download was successful
        :rtype: bool
        """
        gallery_pages = self.get_links_from_gallery(f"https://www.transfur.com/Users/{section}/Gallery")
        for gallery_page in gallery_pages:
            self.download_submission(gallery_page["section"], directory)
        return True

    def download_sketches(self, section:str, directory:str) -> bool:
        """
        Attempt to download a Transfur sketches gallery.
        
        :param section: Section of URL used to get the gallery, should be Transfur username
        :type section: str, required
        :param directory: Directory to save files into
        :type directory: str, required
        :return: Whether download was successful
        :rtype: bool
        """
        sketch_pages = self.get_links_from_gallery(f"https://www.transfur.com/Users/{section}/Sketches")
        for sketch_page in sketch_pages:
            self.download_submission(sketch_page["section"], directory)
        return True
    
    def download_favorites(self, section:str, directory:str) -> bool:
        """
        Attempt to download a Transfur favorites gallery.
        
        :param section: Section of URL used to get the gallery, should be Transfur username
        :type section: str, required
        :param directory: Directory to save files into
        :type directory: str, required
        :return: Whether download was successful
        :rtype: bool
        """
        favorites_pages = self.get_links_from_gallery(f"https://www.transfur.com/Users/{section}/Favorites")
        for favorites_page in favorites_pages:
            self.download_submission(favorites_page["section"], directory)
        return True
    
    def download_tag(self, section:str, directory:str) -> bool:
        """
        Attempt to download all submissions of a given Transfur tag.
        
        :param section: Section of URL used to get the gallery, should be Transfur tag
        :type section: str, required
        :param directory: Directory to save files into
        :type directory: str, required
        :return: Whether download was successful
        :rtype: bool
        """
        tag_pages = self.get_links_from_gallery(f"https://www.transfur.com/Tags/{section}")
        for tag_page in tag_pages:
            self.download_submission(tag_page["section"], directory)
        return True
    
    def download_user(self, section:str, directory:str) -> bool:
        """
        Attempt to download a Transfur galleries from a given user.
        
        :param section: Section of URL used to get the gallery, should be Transfur username
        :type section: str, required
        :param directory: Directory to save files into
        :type directory: str, required
        :return: Whether download was successful
        :rtype: bool
        """
        if "gallery" in self.include:
            self.download_gallery(section, directory)
        if "sketches" in self.include:
            self.download_sketches(section, directory)
        if "favorites" in self.include:
            self.download_favorites(section, directory)
        return True
    
    def get_id(self, url:str) -> str:
        """
        Gets the id for a Transfur page.

        :param url: Transfur comic page URL
        :type url: str, required
        :return: ID for the comic URL
        :rtype: str
        """
        new_url = re.sub(r"\/+$", "", url.lower())
        artist = re.findall(r"(?<=transfur.com\/users\/)[^\/]+", new_url)[0]
        number = re.findall(r"(?<=\/)[0-9]+$|(?<=\/)[0-9]+\/[0-9]+$", new_url)[0]
        if not "/" in number:
            number = f"{number}/1"
        submission_number = int(re.findall("^[0-9]+", number)[0])
        image_number = int(re.findall("[0-9]+$", number)[0])
        return f"transfur-{artist}-{submission_number}-{image_number}"
    
    def archive_contains_all(self, page_url:str, num_images:int) -> bool:
        """
        Returns whether the archive contains IDs for every image in a sequence for a media page.

        :param page_url: Transfur media page
        :type page_url: str, required
        :param num_images: Number of images in the sequence
        :type num_images: int, required
        :return: Whether the archive contains IDs for every image
        :rtype: bool
        """
        identifier = re.findall(".+-(?=[0-9]+$)", self.get_id(page_url))[0]
        for i in range(1, num_images+1):
            if not self.archive_contains(f"{identifier}{i}"):
                return False
        return True
    
    def get_links_from_gallery(self, url:str) -> List[dict]:
        """
        Returns a list of links from a given Tranfur gallery.
        Links are given as dicts with "url" and "num_images" keys.
        Doesn't include already downloaded pages.

        :param url: URL of the Transfur gallery to scan
        :type url: str, required
        :return: List of links in the transfur gallery
        :rtype: list[dict]
        """
        i = 0
        links = []
        gallery_pages = [url]
        while i < len(gallery_pages):
            # Load gallery URL
            self.initialize()
            self.cookies_to_header()
            bs = self.web_get(gallery_pages[i])
            i += 1
            # Get list of media links on the current page
            gallery_items = bs.find_all("div", {"class":"galleryItem"})
            for gallery_item in gallery_items:
                # Get the page link
                title = gallery_item.find("span", {"class":"title"})
                current_link = "https://www.transfur.com" + title.find("a")["href"]
                # Get the number of pages
                try:
                    statistics = gallery_item.find("span", {"class":"statistics"}).get_text()
                    images_text = re.findall(r"[0-9]+\s+images", statistics)[0]
                    num_images = int(re.findall("^[0-9]+", images_text)[0])
                except IndexError:
                    num_images = 1
                # Add link to the list
                section = re.findall(self.sub_section, current_link.lower())[0]
                links.append({"section":section, "num_images":num_images})
            # Get more gallery pages
            try:
                page_container = bs.find("span", {"class":"pageList"})
                gallery_links = page_container.find_all("a")
                for gallery_link in gallery_links:
                    current_link = "https://www.transfur.com" + gallery_link["href"]
                    if not current_link in gallery_pages:
                        gallery_pages.append(current_link)
            except AttributeError: pass
        # Remove already downloaded links
        for i in range(len(links)-1, -1, -1):
            if self.archive_contains_all("transfur.com/users/" + links[i]["section"], links[i]["num_images"]):
                del links[i]
        # Return list of links
        return links

    def get_info_from_page(self, section:str) -> List[dict]:
        """
        Returns a list of dictionaries containing metadata for a given Transfur media page.
        Contains multiple dictionaries if there are multiple pages in the sequence.

        :param section: Section of the tranfur submission URL containing info linking to the submission.
        :type url: str, required
        :return: List of dictionaries containing metadata for the given media page
        :rtype: list[dict]
        """
        # Load page URL
        self.initialize()
        self.cookies_to_header()
        base_url = f"https://www.transfur.com/users/{section}".lower()
        bs = self.web_get(base_url)
        # Get title
        try:
            title = ""
            base_page = dict()
            details = bs.find("div", {"class":"galleryImageDetails"})
            title_element = details.find("h2", {"class":"title"})
            for text_element in title_element.find_all(string=True):
                if not text_element.parent.name == "a":
                    title = title + text_element.get_text()
            title = re.sub(r"\s+by\s*$", "", title)
            base_page["title"] = re.sub(r"^\s+|\s+$", "", title)
        except AttributeError:
            # Return empty list of links if page not properly loaded
            return []
        # Get artist
        artist_element = title_element.find("a")
        base_page["artist"] = re.sub(r"^\s+|\s+$", "", artist_element.get_text())
        # Get statistics
        statistics = bs.find("p", {"class":"statistics"})
        stat_elements = statistics.find_all("span")
        base_page["views"] = None
        base_page["favorites"] = None
        for stat_element in stat_elements:
            stat_text = stat_element.get_text().lower()
            if "date:" in stat_text:
                # Get date
                base_page["date"] = gallery_dvk.extractor.extractor.get_date(stat_text, "mdy")
            if "views:" in stat_text:
                # Get Views
                base_page["views"] = int(re.findall("[0-9]+", stat_text)[0])
            if "favorites:" in stat_text:
                # Get Favorites
                base_page["favorites"] = int(re.findall("[0-9]+", stat_text)[0])
        # Get tags
        base_page["tags"] = []
        tag_elements = bs.find("p", {"class":"tags"}).find_all("a")
        for tag_element in tag_elements:
            base_page["tags"].append(tag_element.get_text())
        if base_page["tags"] == []:
            base_page["tags"] = None
        # Get description
        description_element = bs.find("div", {"class":"description"})
        description = re.sub(r"^<div[^>]+>\s+|\s+<\/div>$", "", str(description_element))
        base_page["description"] = description
        # Find all pages in a sequence
        pages = []
        try:
            thumbnails = bs.find("div", {"class":"galleryImageSequenceList"}).find_all("a")
            for thumbnail in thumbnails:
                thumb_url = str(thumbnail["href"]).lower()
                thumb_url = re.sub("/+$", "", f"https://www.transfur.com{thumb_url}")
                pages.append({"url":thumb_url})
        except AttributeError:
            # Add original URL if no sequence list found
            pages.append({"url":base_url})
        base_page["total_images"] = len(pages)
        # Get info for each page of the sequence
        for i in range(0, len(pages)):
            # Add all existing info from the base_page
            for item in base_page.items():
                pages[i][item[0]] = item[1]
            # Load the current page if necessary
            if len(pages) > 1:
                self.cookies_to_header()
                bs = self.web_get(pages[i]["url"])
            # Get the image url
            image = bs.find("img", {"id":"galleryImage"})
            pages[i]["image_url"] = "https://www.transfur.com" + image["src"].lower()
            # Get the submission id
            identifier = self.get_id(pages[i]["url"])
            pages[i]["id"] = re.findall("[0-9]+-[0-9]+$", identifier)[0]
            # Get the page number
            pages[i]["image_number"] = int(re.findall("[0-9]+$", identifier)[0])
        # Return pages
        return pages
    
    def download_page(self, page:dict, directory:str) -> str:
        """
        Downloads a given Transfur comic page.
    
        :param page: Metadata dict for a given Transfur page.
        :type page: dict, required
        :param directory: Directory to save files into
        :type directory: str, required
        :return: Path of the media file created, if applicable
        :rtype: str
        """
        subs = ["Transfur", page["artist"]]
        return super().download_page(page, directory, subs)
    
    def login(self, username:str, password:str) -> bool:
        """
        Attempts to login the requests_session object to Transfur.com

        :param username: Transfur username
        :type username: str, required
        :param password: Transfur password
        :type password: str, required
        :return: Whether login was successful
        :rtype: bool
        """
        # Load the login page to get request verification cookies
        bs = self.web_get("https://www.transfur.com/Account/Login")
        input_element = bs.find("input", {"name":"__RequestVerificationToken"})
        # Attempt login
        request = {"__RequestVerificationToken":input_element["value"]}
        request["UsernameOrEmail"] = username
        request["Password"] = password
        headers = {"Content-Type":"application/x-www-form-urlencoded"}
        response = self.requests_session.post("https://www.transfur.com/Account/Login", headers=headers, data=request)
        # Move to main Transfur page
        self.cookies_to_header()
        bs = self.web_get("https://www.transfur.com/")
        # Check whether login was successful
        member_links = bs.find("div", {"class":"memberLinks"})
        menu_header = member_links.find("a", {"class":"menuHeader"})
        self.attempted_login = True
        return menu_header is not None
    
    def user_login(self) -> bool:
        """
        Asks user for Transfur.com login information before attempting login.
        """
        super().user_login("Transfur")