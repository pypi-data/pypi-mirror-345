#!/usr/bin/env python3

import re
import operator
import gallery_dvk.extractor.extractor
from typing import List

class KemonoCafe(gallery_dvk.extractor.extractor.Extractor):
    def __init__(self, config_paths:List[str]=gallery_dvk.config.get_default_config_paths()):
        """
        Creates the KemonoCafe object and loads configuration files.
        
        :param config_paths: Paths to attempt to read as a configuration file, defaults to default config paths
        :type config_paths: list[str]
        """
        super().__init__(category="kemonocafe", config_paths=config_paths)
        # Set the URL matchers
        self.url_matchers = []
        sub_match = r"(?:https?:\/\/)?(?:www\.)?[a-z\-]+\.kemono\.cafe\/comic\/[a-z0-9\-]+\/?"
        self.sub_section = r"[a-z\-]+\.kemono.cafe\/comic\/[a-z0-9\-]+"
        self.url_matchers.append({"match":sub_match, "section":self.sub_section, "type":"comic_page"})
        archive_match = r"(?:https?:\/\/)?(?:www\.)?[a-z\-]+\.kemono\.cafe(?:\/archive)?\/?"
        archive_section = r"[a-z\-]+(?=\.kemono\.cafe)"
        self.url_matchers.append({"match":archive_match, "section":archive_section, "type":"archive"})
        # Set the default filename format, if necessary
        if self.filename_format == "{title}":
            self.filename_format = "{id}"

    def download_comic_page(self, section:str, directory:str) -> bool:
        """
        Attempt to download a Kemono Cafe comic page.
        
        :param section: Section of URL used to get submission, should contain submission ID
        :type section: str, required
        :param directory: Directory to save files into
        :type directory: str, required
        :return: Whether download was successful
        :rtype: bool
        """
        page = self.get_page_info(section)
        self.download_page(page, directory) 
        return True
    
    def download_archive(self, section:str, directory:str) -> bool:
        """
        Attempt to download all comic pages from Kemono Cafe archive.
        
        :param section: Section of URL used to get comic archive, should contain comic name
        :type section: str, required
        :param directory: Directory to save files into
        :type directory: str, required
        :return: Whether download was successful
        :rtype: bool
        """
        chapters = self.get_chapter_info(section)
        links = self.get_comic_pages(section)
        for link in links:
            page = self.get_page_info(link, chapters)
            self.download_page(page, directory) 
        return True

    def get_id(self, url:str) -> str:
        """
        Gets the id for a Kemono Cafe page.

        :param url: Kemomo Cafe comic page URL
        :type url: str, required
        :return: ID for the comic URL
        :rtype: str
        """
        page = re.findall(r"(?<=kemono\.cafe\/comic\/)[^\/]+", url.lower())[0]
        comic = re.findall(r"[a-z\-]+(?=\.kemono\.cafe\/comic\/)", url.lower())[0]
        return f"kemonocafe-{comic}-{page}"

    def get_comic_pages(self, section:str) -> List[str]:
        """
        Returns a list of pages for a given KemonoCafe comic.

        :param section: Section of KemonoCafe URL, should be the name of the comic
        :type section: str, required
        :return: List of comic pages, with only the necessary section
        :rtype: list[str]
        """
        page_num = 0
        comic_pages = []
        archive_pages = [f"https://{section}.kemono.cafe/comic/"]
        while page_num < len(archive_pages):
            # Load Page
            bs = self.web_get(archive_pages[page_num])
            print(archive_pages[page_num])
            page_num += 1
            # Get list of comic page links
            articles = bs.find_all("article")
            for article in articles:
                header = article.find("h2", {"class":"entry-title"})
                page_section = re.findall(self.sub_section, header.find("a")["href"])[0]
                comic_pages.append(page_section)
            # Find more archive pages
            archive_links = bs.find_all("a", {"class":"page-numbers"})
            for archive_link in archive_links:
                if archive_link["href"] not in archive_pages:
                    archive_pages.append(archive_link["href"])
        # Sort comic pages
        comic_pages = sorted(comic_pages)
        # Remove already downloaded pages
        for i in range(len(comic_pages)-1, -1, -1):
            if self.archive_contains(self.get_id(comic_pages[i])):
                del comic_pages[i]
        return comic_pages

    def get_chapter_info(self, section:str) -> List[dict]:
        """
        Returns info for all the chapters in a given Kemono Cafe comic.

        :param section: Section of KemonoCafe URL, should be the name of the comic
        :type section: str, required
        :return: List of chapters with dictionaries containing chapter info
        :rtype: list[dict]
        """
        # Load archive page
        bs = self.web_get(f"https://{section}.kemono.cafe/archive/")
        # Get the chapter sections
        chapters = []
        chapter_containers = bs.find_all("div", {"class":"comic-archive-chapter-wrap"})
        for container in chapter_containers:
            # Get chapter title and description
            title = container.find("h3", {"class":"comic-archive-chapter"}).get_text()
            description = container.find("div", {"class":"comic-archive-chapter-description"}).get_text()
            if description == "":
                description = None
            # Get chapter date
            date_container = container.find("span", {"class":"comic-archive-date"})
            date = gallery_dvk.extractor.extractor.get_date(date_container.get_text())
            # Get listed pages in the chapter
            links = []
            link_containers = container.find_all("a")
            for link_container in link_containers:
                page_section = re.findall(self.sub_section, link_container["href"])[0]
                links.append(page_section)
            # Add chapter info
            chapters.append({"title":title, "date":date, "description":description, "links":links})
        # Return chapters
        return sorted(chapters, key=operator.itemgetter("date"))

    def get_page_info(self, section:str, chapters:List[dict]=None) -> dict:
        """
        Returns a dict containing info for a given Kemono Cafe comic page.

        :param section: Section of URL containing info for the comic page
        :type section: str, requried
        :param chapters: Chapter info for the comic as returned by get_chapter_info, defaults to None
        :type chapters: list[dict], optional
        :return: Dictionary containing metadata info about the comic page
        :rtype: dict
        """
        # Get the URL for the page
        url = f"https://{section}/"
        # Load the URL
        bs = self.web_get(url)
        # Update to the proper URL if redirected
        canonical = bs.find("link", {"rel":"canonical"})
        url = re.findall(self.sub_section, canonical["href"])[0]
        url = f"https://{url}/"
        page = {"url":url}
        # Get the ID for the page
        identifier = self.get_id(url)
        page["id"] = identifier[identifier.find("-")+1:]
        # Get the page title
        page["title"] = bs.find("h1", {"class":"entry-title"}).get_text()
        # Get the image_url
        comic_container = bs.find("div", {"id":"comic"})
        image = comic_container.find("img")
        page["image_url"] = image["src"]
        # Get the page title
        page["tagline"] = bs.find("title", string=re.compile(r"[\|:]")).get_text()
        page["comic"] = re.findall(r"^[^\|:]+(?=[\|:])", page["tagline"])[0]
        page["comic"] = re.sub(r"^\s+|\s+$", "", page["comic"])
        try:
            page["author"] = re.findall(r"(?<=\sby\s)[A-z0-9\s]+$", page["tagline"])[0]
        except IndexError: page["author"] = None
        # Get the date from the image file
        try:
            regex = r"(?<=\/)[0-9]{4}-[0-1][0-9]-[0-3][0-9](?=[^0-9])"
            date_string = re.findall(regex, page["image_url"])[0]
            page["date"] = gallery_dvk.extractor.extractor.get_date(date_string, "ymd")
        except IndexError:
            regex = r"(?<=\/)[0-3]?[0-9]\/[0-9]{4}\/[0-1]?[0-9](?=\/)"
            date_string = re.findall(regex, page["image_url"])[0]
            page["date"] = gallery_dvk.extractor.extractor.get_date(date_string, "dym")
        # Load chapter info, if necessary
        loaded_chapters = chapters
        if loaded_chapters is None:
            loaded_chapters = self.get_chapter_info(section[:section.find(".")])
        # Get the oldest available chapter
        page["chapter"] = None
        page["chapter_description"] = None
        for chapter in loaded_chapters:
            if page["date"] >= chapter["date"] or section in chapter["links"]:
                page["chapter"] = chapter["title"]
                page["chapter_description"] = chapter["description"]
                # Check if the chapter matches exactly
                if section in chapter["links"]:
                    break
        # Get post content
        page["post_content"] = None
        post_content = bs.find("div", {"class":"post-content"})
        try:
            # Get the main post content
            assert post_content is not None
            content = str(post_content).replace("\r","\n")
            content = content.replace("\n", " ")
            content = re.sub(r"^\s*<div[^<]+>\s*|\s*<\/div>\s*$", "", content)
            content = re.sub(r"^<header>.+<\/header>\s*", "", content)
            content = re.sub(r"\s*<p>\s*", "<p>", content)
            content = re.sub(r"\s*<\/p>\s*", "</p>", content)
            page["post_content"] = content
            # Get the date
            date_string = post_content.find("span", {"class":"date"}).get_text()
            page["date"] = gallery_dvk.extractor.extractor.get_date(date_string)
            # Get the author
            author = post_content.find("span", {"class":"author"}).get_text()
            author = re.sub(r"^\s+|\s+$", "", author)
            if not page["author"].lower() == author.lower():
                page["author"] = author
        except (AssertionError, AttributeError): page["post_content"] = None
        if page["post_content"] == "":
            page["post_content"] = None
        # Return the page
        return page

    def download_page(self, page:dict, directory:str) -> str:
        """
        Downloads a given Kemono Cafe comic page.
    
        :param page: Metadata dict for a given Kemono Cafe page.
        :type page: dict, required
        :param directory: Directory to save files into
        :type directory: str, required
        :return: Path of the media file created, if applicable
        :rtype: str
        """
        subs = ["KemonoCafe", page["comic"], page["chapter"]]
        return super().download_page(page, directory, subs)
