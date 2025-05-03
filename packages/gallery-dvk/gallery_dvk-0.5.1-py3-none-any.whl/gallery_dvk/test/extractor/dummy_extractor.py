#!/usr/bin/env python3

import gallery_dvk.extractor.extractor
from typing import List

class DummyExtractor(gallery_dvk.extractor.extractor.Extractor):
    def __init__(self, config_paths:List[str]=[]):
        """
        Creates a TestExtractor object and loads configuration files.
        
        :param config_paths: Paths to attempt to read as a configuration file, defaults to default config paths
        :type config_paths: list[str]
        """
        super().__init__(category="transfur", config_paths=config_paths)
        # Set the URL matchers
        self.url_matchers = []
        match = r"(?:https:\/\/)?(?:www\.)pythonscraping.com\/.+"
        section = r".+"
        self.url_matchers.append({"match":match, "section":section, "type":"url"})
        # Set the default include values if necessary
        if self.include == []:
            self.include = ["gallery", "sketches"]
    
    def download_url(self, section:str, directory:str) -> bool:
        """
        Downloads the given URL.
        
        :param section: Full URL to download
        :type section: str, required
        :param directory: Directory to save into
        :type directory: str, required
        :return: Whether the download was successful
        :rtype: bool
        """
        page = {"title":"Test Title!", "url":section}
        self.download_page(page, directory)
        return True