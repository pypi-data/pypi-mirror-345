#!/usr/bin/env python3

import os
import re
import shutil
import tempfile
import html_string_tools
import gallery_dvk.extractor.extractor
import metadata_magic.file_tools as mm_file_tools
import metadata_magic.rename as mm_rename
from os.path import abspath, basename, exists, join
from typing import List

tag_alias = {"":""}
tag_alias["slow"] = "Slow Growth"
tag_alias["fast"] = "Fast Growth"
tag_alias["instant"] = "Instant Growth"

tag_alias["magic"] = "Magic"
tag_alias["chem"] = "Chemical"
tag_alias["science"] = "Science"

tag_alias["ag"] = "Ass Growth"
tag_alias["fa"] = "Fat Growth"
tag_alias["gts"] = "Giantess"
tag_alias["hg"] = "Hair Growth"
tag_alias["lg"] = "Leg Growth"
tag_alias["mg"] = "Female Muscle Growth"
tag_alias["mm"] = "Male Muscle Growth"
tag_alias["mpg"] = "Male Penis Growth"
tag_alias["multiple"] = "Multi-Breast"

tag_alias["bg"] = ""
tag_alias["big"] = "Realistic Breast Size"
tag_alias["huge"] = "Unrealistic Breast Size"
tag_alias["wow"] = "Room-Filling Breasts"

tag_alias["ft"] = "Female-to-Male"
tag_alias["tg"] = "Male-to-Female"

tag_alias["aliens"] = "Aliens"
tag_alias["ar"] = "Age Regression"
tag_alias["bond"] = "Bondage"
tag_alias["cb"] = "Clothes Ripping"
tag_alias["hyp"] = "Hypnosis"
tag_alias["inc"] = "Incect"
tag_alias["lac"] = "Lactation"
tag_alias["ment"] = "Mental Transformation"
tag_alias["nc"] = "Non-Consensual"
tag_alias["offstage"] = "Events Offstage"
tag_alias["preg"] = "Pregnancy"
tag_alias["rc"] = "Remote-Controlled"
tag_alias["sc"] = "Self-Controlled"
tag_alias["shem"] = "She-Male"
tag_alias["weird"] = "Weird Transformations"
tag_alias["asleep"] = "Asleep Subject"


class OverflowingBra(gallery_dvk.extractor.extractor.Extractor):
    def __init__(self, config_paths:List[str]=gallery_dvk.config.get_default_config_paths()):
        """
        Creates the OverflowingBra object and loads configuration files.
        
        :param config_paths: Paths to attempt to read as a configuration file, defaults to default config paths
        :type config_paths: list[str]
        """
        super().__init__(category="overflowingbra", config_paths=config_paths)
        # Set the URL matchers
        self.url_matchers = []
        gallery_match = r"(?:https?:\/\/)?(?:www\.)?overflowingbra\.com\/[^\/]+\/?"
        gallery_section = r"(?<=overflowingbra\.com\/)[^\/]+"
        self.url_matchers.append({"match":gallery_match, "section":gallery_section, "type":"gallery"})
        if self.webpage_sleep == 1.5:
            self.webpage_sleep = 3
        if self.download_sleep == 1.5:
            self.download_sleep = 2.5

    def get_id(self, url:str) -> str:
        """
        Gets the id for an OverflowingBra story.

        :param url: OverflowengBra story page URL
        :type url: str, required
        :return: ID for the story URL
        :rtype: str
        """
        identifier = re.findall(r"(?<=storyid=)[0-9]+", url.lower())[0]
        return f"overflowingbra-{identifier}"

    def download_gallery(self, section:str, directory:str) -> bool:
        """
        Attempt to download stories from an OverflowingBra gallery.
        
        :param section: Section of URL used to get stories
        :type section: str, required
        :param directory: Directory to save files into
        :type directory: str, required
        :return: Whether download was successful
        :rtype: bool
        """
        stories = self.get_stories(section)
        for story in stories:
            self.download_page(story, directory)
        return True

    def get_stories(self, section:str) -> List[dict]:
        """
        Returns a list of dictionaries with story metadata and download links.

        :param section: Section of OverflowingBra URL indicating the gallery
        :type section: str, required
        :return: List of metadata for all the stories on the page
        :rtype: List[dict]
        """
        # Get the list of stories on the page
        bs = self.web_get(f"https://overflowingbra.com/{section}")
        storyboxes = bs.find_all("div", {"class":"storybox"})
        stories = []
        # Run through each story
        for storybox in storyboxes:
            # Get the title and URL
            title_element = storybox.find("div", {"class":"storytitle"}).find("a")
            url = "https://overflowingbra.com/" + title_element["href"]
            story = {"title":title_element.get_text().strip(), "url":url}
            # Get the ID
            story["id"] = self.get_id(url).replace("overflowingbra-", "")
            # Get the author
            author_element = storybox.find("div", {"class":"author"}).find("a")
            story["author"] = author_element.get_text().strip()
            # Get the date
            try:
                date_string = storybox.find("div", {"class":"submitdate"}).get_text()
                year = re.findall(r"[0-9]{2}\s|[0-9]{2}\s*$", date_string)[0]
                if int(year) > 80:
                    year = f"19{year}"
                else:
                    year = f"20{year}"
                date_string = re.sub(r"[0-9]{2}\s|[0-9]{2}\s*$", year, date_string)
                story["date"] = gallery_dvk.extractor.extractor.get_date(date_string)
            except IndexError: story["date"] = None
            # Get tags
            tag_string = storybox.find("div", {"class":"storycodes"}).get_text().strip()
            tags = re.sub(r"\s+", ",", tag_string.lower()).split(",")
            for i in range(len(tags)-1, -1, -1):
                tags[i] = tag_alias[tags[i]]
                if tags[i] == "":
                    del tags[i]
            story["tags"] = tags
            if story["tags"] == []:
                story["tags"] = None
            # Get summary
            summary_element = storybox.find("div", {"class":"summary"})
            story["summary"] = summary_element.get_text().strip()
            if story["summary"] == "":
                story["summary"] = None
            # Get the number of downloads
            download_text = storybox.find("div", {"class":"downloads"}).get_text()
            story["downloads"] = int(re.findall(r"[0-9]+", download_text)[0])
            # Append story to the list of stories
            stories.append(story)
        # Return Stories
        return stories

    def download_page(self, page:dict, directory:str) -> str:
        """
        Downloads a given OverflowingBra page.
    
        :param page: Metadata dict for a given OverflowingBra page.
        :type page: dict, required
        :param directory: Directory to save files into
        :type directory: str, required
        :return: Path of the media file created, if applicable
        :rtype: str
        """
        # Download the page
        subs = ["OverflowingBra", page["author"]]
        media_file = super().download_page(page, directory, subs)
        # Return if none
        if media_file is None:
            return None
        # Replace extension with zip
        parent_dir = abspath(join(media_file, os.pardir))
        filename = re.findall(r".+(?=\.[^.]+$)", basename(media_file))[0]
        zip_media = abspath(join(parent_dir, f"{filename}.zip"))
        shutil.move(media_file, zip_media)
        # Extract ZIP into a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            mm_file_tools.extract_zip(zip_media, temp_dir,  remove_internal=True)
            files = os.listdir(temp_dir)
            # Return the ZIP file if it contains more than one file
            if not len(files) == 1:
                return zip_media
            # Rename the extracted file
            extracted_file = abspath(join(temp_dir, files[0]))
            extension = html_string_tools.get_extension(extracted_file)
            filename = mm_rename.get_available_filename([extracted_file], filename, parent_dir)
            new_file = abspath(join(parent_dir, f"{filename}{extension}"))
            shutil.move(extracted_file, new_file)
        assert exists(new_file)
        # Delete the old ZIP file
        os.remove(zip_media)
        # Return the extracted file
        return new_file
