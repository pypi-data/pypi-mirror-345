#!/usr/bin/env python3

import os
import re
import copy
import math
import operator
import gallery_dvk.extractor.extractor
import metadata_magic.file_tools as mm_file_tools
from PIL import Image
from os.path import abspath, exists, join
from typing import List

def stitch_images(top_image:Image, bottom_image:Image) -> Image:
    """
    Stitches two images into one image, with the originals stacked on top of each other vertically.
    
    :param top_image: Image to place on top
    :type top_image: Image, required
    :param bottom_image: Image to place on bottom
    :type bottom_image: Image, required
    :return: Images stitched together, stacked vertically
    :rtype: Image
    """
    # Get the sizes of the images
    t_width, t_height = top_image.size
    b_width, b_height = bottom_image.size
    # Create the new image
    height = t_height + b_height
    width = t_width
    if b_width > t_width:
        width = b_width
    stitched = Image.new("RGB", (width, height), "#ffffff")
    # Paste the top image
    x = int(math.floor((width - t_width)/2))
    stitched.paste(top_image, (x, 0, x+t_width, t_height))
    # Paste the bottome image
    x = int(math.floor((width - b_width)/2))
    stitched.paste(bottom_image, (x, t_height, x+b_width, height))
    # Return the stitched image
    return stitched

class Webtoon(gallery_dvk.extractor.extractor.Extractor):
    def __init__(self, config_paths:List[str]=gallery_dvk.config.get_default_config_paths()):
        """
        Creates the Webtoon object and loads configuration files.
        
        :param config_paths: Paths to attempt to read as a configuration file, defaults to default config paths
        :type config_paths: list[str]
        """
        super().__init__(category="webtoon", config_paths=config_paths)
        # Set the URL matchers
        self.url_matchers = []
        toon_match = r"^(?:https?:\/\/)?(?:www\.)?webtoons.com\/[a-z]{2}\/.+\/list\?title_no=[0-9]+(?:&page=[0-9]+)?\/?$"
        toon_section = r"(?<=webtoons\.com\/).+list\?title_no=[0-9]+"
        self.url_matchers.append({"match":toon_match, "section":toon_section, "type":"toon"})
        episode_match = r"^(?:https?:\/\/)?(?:www\.)?webtoons.com\/[a-z]{2}\/.+\/viewer\?title_no=[0-9]+&episode_no=[0-9]+\/?$"
        self.episode_section = r"(?<=webtoons.com\/)[a-z]{2}\/.+\/viewer\?title_no=[0-9]+&episode_no=[0-9]+"
        self.url_matchers.append({"match":episode_match, "section":self.episode_section, "type":"episode"})
        # Set the default filename format, if necessary
        if self.filename_format == "{title}":
            self.filename_format = "{id}_{title}"
    
    def initialize(self):
        """
        Initializes the requests session and sqlite archive database.
        Does nothing if objects are already created.
        """
        # Do the default extractor initialize
        super().initialize()
        # Set the headers to use webtoons.com as a referer
        headers = self.requests_session.headers.update({"Referer":"https://www.webtoons.com/"})
    
    def get_info_from_config(self, config:dict, category:str):
        """
        Sets variables in the Extractor object based on values in a given config dictionary.
        
        :param config: Dictionary containing gallery-dvk config info
        :type config: dict, required
        :param category: Category of extractor to search config file for
        :type category: str, required
        """
        super().get_info_from_config(config, "webtoon")
        # Get whether to stitch images from an episode together
        self.stitch_images = gallery_dvk.extractor.extractor.get_category_value(config, category, "stitch_images", [bool], True)
        # Get whether to delete individual images if a stitched image is created
        self.only_stitched = gallery_dvk.extractor.extractor.get_category_value(config, category, "only_stitched", [bool], False)
    
    def get_id(self, url:str) -> str:
        """
        Gets the id for a Webtoon page.

        :param url: Webtoon comic page URL
        :type url: str, required
        :return: ID for the comic URL
        :rtype: str
        """
        section = re.findall(self.episode_section, url.lower())[0]
        language_code = section[:2]
        title_code = re.findall(r"(?<=viewer\?title_no=)[0-9]+", section)[0]
        episode_code = re.findall(r"(?<=&episode_no=)[0-9]+(?=\/?$)", section)[0]
        return f"webtoon-{language_code}-t{title_code}-e{episode_code}"
    
    def download_episode(self, section:str, directory:str) -> bool:
        """
        Attempt to download a Webtoon episode.
        
        :param section: Section of URL used to get submission, should contain episode ID
        :type section: str, required
        :param directory: Directory to save files into
        :type directory: str, required
        :return: Whether download was successful
        :rtype: bool
        """
        pages = self.get_episode_info(section)
        self.download_episode_images(pages, directory)
        return True
    
    def download_toon(self, section:str, directory:str) -> bool:
        """
        Attempt to download all the episodes for a given Webtoon.
        
        :param section: Section of URL used to get submission, should contain Webtoon title ID
        :type section: str, required
        :param directory: Directory to save files into
        :type directory: str, required
        :return: Whether download was successful
        :rtype: bool
        """
        episodes = self.get_episodes(section)
        for episode in episodes:
            episode_section = re.findall(self.episode_section, episode["url"])[0]
            pages = self.get_episode_info(episode_section, episode)
            self.download_episode_images(pages, directory)
        return True
    
    def get_episodes(self, section:str) -> List[dict]:
        """
        Returns a list of episodes for a given Webtoons comic.
        Also returns comic and episode info in dictionaries
        
        :param section: Section of a webtoons comic url containing identifying information
        :type section: str, required
        :return: List of dictionaries containing links and info for all the episodes of a comic
        :rtype: list[dict]
        """
        # Load page
        bs = self.web_get(f"https://www.webtoons.com/{section}")
        # Get the webtoon title
        detail_header = bs.find("div", {"class":"detail_header"})
        title_element = detail_header.find(attrs={"class":"subj"})
        base = {"webtoon":re.sub(r"^\s+|\s+$", "", title_element.get_text())}
        # Get the webtoon genre
        genre_element = detail_header.find(attrs={"class":"genre"})
        base["genre"] = re.sub(r"^\s+|\s+$", "", genre_element.get_text())
        # Get the webtoon authors(s)
        authors = []
        author_elements = detail_header.find_all("a", {"class":"author"})
        for author_element in author_elements:
            authors.append(re.sub(r"^\s+|\s+$", "", author_element.get_text()))
        base["authors"] = authors
        # Get the webtoon view count
        aside = bs.find("div", {"id":"_asideDetail"})
        view_icon = aside.find("span", {"class":"ico_view"})
        view_element = view_icon.parent.find("em", {"class":"cnt"})
        view_string = re.sub(r"^\s+|\s+$", "", view_element.get_text()).lower()
        view_num = float(re.findall(r"^[0-9\.,]+", view_string)[0].replace(",", "."))
        if "k" in view_string:
            view_num = view_num * 1000
        elif "m" in view_string:
            view_num = view_num * 1000000
        elif "b" in view_string:
            view_num = view_num * 1000000000
        base["webtoon_views"] = int(view_num)
        # Get the webtoon subscriber count
        subscribe_icon = aside.find("span", {"class":"ico_subscribe"})
        subscribe_element = subscribe_icon.parent.find("em", {"class":"cnt"})
        subscribe_string = re.sub(r"^\s+|\s+$", "", subscribe_element.get_text())
        subscribe_string = re.sub(r"[\.,]", "", subscribe_string)
        base["webtoon_subscribers"] = int(subscribe_string)
        # Get the webtoon rating
        rating_element = aside.find("em", {"id":"_starScoreAverage"})
        rating_string = re.sub(r"^\s+|\s+$", "", rating_element.get_text()).replace(",", ".")
        base["webtoon_rating"] = float(rating_string)
        # Get the webtoon summary
        summary_element = bs.find("p", {"class":"summary"})
        base["webtoon_summary"] = re.sub(r"^\s+|\s+$", "", summary_element.get_text())
        # Run through each page of episodes
        i = 0
        episodes = []
        gallery_pages = [f"https://www.webtoons.com/{section}&page=1"]
        while True:
            # Get list of episode pages
            episode_elements = bs.find_all("li", {"class":"_episodeItem"})
            for episode_element in episode_elements:
                # Add all existing info from the base_page
                episode = dict()
                for item in base.items():
                    episode[item[0]] = item[1]
                # Get the episode number
                episode["episode"] = int(episode_element["data-episode-no"])
                # Get the episode title
                title_element = episode_element.find("span", {"class":"subj"}).find("span")
                episode["title"] = re.sub(r"^\s+|\s+$", "", title_element.get_text())
                # Get the episode date
                date_element = episode_element.find("span", {"class":"date"})
                episode["date"] = gallery_dvk.extractor.extractor.get_date(date_element.get_text())
                # Get the episode likes
                like_element = episode_element.find("span", {"class":"like_area"})
                like_string = re.findall(r"[0-9\.,]+", like_element.get_text())[0]
                like_string = re.sub(r"[\.,]", "", like_string)
                episode["likes"] = int(like_string)
                # Get the episode link
                episode["url"] = episode_element.find("a")["href"]
                # Add episode
                episodes.append(episode)
            # Find the next pages in the gallery
            paginate = bs.find("div", {"class":"paginate"})
            gallery_elements = paginate.find_all("a")
            for element in gallery_elements:
                link = "https://www.webtoons.com" + element["href"]
                if "&page=" in link and not link in gallery_pages:
                    gallery_pages.append(link)
            # Load the next page
            i += 1
            if i == len(gallery_pages):
                break
            bs = self.web_get(gallery_pages[i])
        # Return the list of episodes
        return sorted(episodes, key=operator.itemgetter("episode"))
    
    def get_episode_info(self, section:str, comic:dict=None) -> List[dict]:
        """
        Returns all info for an episode of a webtoons comic.
        Comic dict should be in the format of episode info as given by get_episodes.
        If comic is None, info for the comic is retrieved from the get_episodes method.
        
        :param section: Section of a Webtoon comic URL containing the identifying info
        :type section: str, required
        :param comic: Comic info dict as returned by get_episodes, defaults to None
        :type comic: dict, optional
        :return: List of dicts containing episode info, one for each image
        :rtype: list[dict]
        """
        # Get info for the comic, if necessary
        base = comic
        if comic is None:
            webtoon_section = re.findall(r".+(?=&episode_no=[0-9]+)", section)[0]
            webtoon_section = re.sub(r"(?<=\/)[^\/]+\/viewer\?(?=title)", "list?", webtoon_section)
            episodes = self.get_episodes(webtoon_section)
            for episode in episodes:
                if re.findall(self.episode_section, episode["url"])[0] == section:
                    base = episode
                    break
        # Get the list of image URLs
        bs = self.web_get(base["url"])
        image_container = bs.find("div", {"id":"_imageList"})
        images = image_container.find_all("img", {"class":"_images"})
        # Create dictionaries for each image
        pages = []
        for i in range(0, len(images)):
            # Set all the already existing comic info
            page = dict()
            for item in base.items():
                page[item[0]] = item[1]
            # Set the image URL
            page["image_url"] = images[i]["data-url"]
            # Set the page ID
            page["image_number"] = i+1
            identifier = re.sub(r"^webtoon-", "", self.get_id(page["url"]))
            page["id"] = identifier + "-" + str(i+1)
            # Add the page to the list
            pages.append(page)
        # Return the list of pages
        return pages
    
    def download_page(self, page:dict, directory:str) -> str:
        """
        Downloads a given Webtoon comic page.
    
        :param page: Metadata dict for a given Webtoon page.
        :type page: dict, required
        :param directory: Directory to save files into
        :type directory: str, required
        :return: Path of the media file created, if applicable
        :rtype: str
        """
        image_number = str(page["image_number"])
        subs = ["Webtoon", page["webtoon"], page["title"]]
        return super().download_page(page, directory, subs, f"-i{image_number}")

    def download_episode_images(self, pages:List[dict], directory:str) -> List[str]:
        """
        Downloads all the images for a given Webtooon episode.
        The episode images will be stitched together if specified in the gallery_dvk config file.
        If specified in the config file, only the stitched file will be included.
        
        :param pages: Webtoons episode pages, as returned by get_episode_info
        :type pages: required, List[dict]
        :param directory: Directory in which to save files
        :type directory: str, required
        :return: List of media files that have been downloaded/created through stitching
        :rtype: List[str]
        """
        # Download media files
        media_files = []
        for page in pages:
            media_file = self.download_page(page, directory)
            if media_file is not None:
                media_files.append(media_file)
        # Stitch media files together, if specified
        if self.stitch_images and len(media_files) > 0:
            images = []
            stitched = None
            for i in range(0, len(media_files)):
                # Load media file
                bottom_image = Image.open(media_files[i])
                # Get info for the image
                image_info = {"image_url": pages[i]["image_url"]}
                image_info["image_number"] = pages[i]["image_number"]
                image_info["id"] = pages[i]["id"]
                image_info["width"] = bottom_image.size[0]
                image_info["height"] = bottom_image.size[1]
                images.append(image_info)
                # Stitch the image
                if stitched is None:
                    stitched = bottom_image
                else:
                    stitched = stitch_images(stitched, bottom_image)
            # Create the metadata for the stitched image
            metadata = copy.deepcopy(pages[0])
            metadata["id"] = re.sub("-[0-9]+$", "", metadata["id"])
            metadata.pop("image_url")
            metadata.pop("image_number")
            metadata["images"] = images
            # Save stitched file
            parent = abspath(join(media_files[0], os.pardir))
            filename = gallery_dvk.extractor.extractor.get_filename_from_page(metadata, parent, self.filename_format)
            stitched_file = abspath(join(parent, f"{filename}.png"))
            stitched.save(stitched_file)
            media_files.append(stitched_file)
            # Save metadata, if applicable
            if self.write_metadata:
                json_file = abspath(join(parent, f"{filename}.json"))
                mm_file_tools.write_json_file(json_file, metadata)
        # Return the list of media files
        if self.stitch_images and self.only_stitched:
            for i in range(len(media_files)-2, -1, -1):
                os.remove(media_files[i])
                json_file = re.sub(r"\.[A-Za-z]+$", ".json", media_files[i])
                if exists(json_file):
                    os.remove(json_file)
                del media_files[i]
        return media_files
