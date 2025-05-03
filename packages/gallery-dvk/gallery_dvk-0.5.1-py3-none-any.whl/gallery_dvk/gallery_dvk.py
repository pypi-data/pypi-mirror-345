#!/usr/bin/env python3

import os
import re
import argparse
import python_print_tools.printer
import metadata_magic.file_tools as mm_file_tools
from gallery_dvk.extractor.docslab import DocsLab
from gallery_dvk.extractor.kemonocafe import KemonoCafe
from gallery_dvk.extractor.overflowingbra import OverflowingBra
from gallery_dvk.extractor.tgcomics import TGComics
from gallery_dvk.extractor.transfur import Transfur
from gallery_dvk.extractor.webtoon import Webtoon
from os.path import abspath, exists

class GalleryDVK():
    def __init__(self):
        """
        Creates the GalleryDVK class.
        """
        self.extractors = []
    
    def __enter__(self):
        """
        Setup for when GallerDVK is opened.
        Create an object for each Extractor.
        """
        self.extractors = [DocsLab(), KemonoCafe(), OverflowingBra(), Transfur(), TGComics(), Webtoon()]
        return self
        
    def __exit__(self, *args):
        """
        Cleanup for GalleryDVK once it is closed.
        """
        for extractor in self.extractors:
            extractor.__exit__()

    def download_from_url(self, url:str, directory:str) -> bool:
        """
        Attepts to download media from a given URL.
        Returns False if the URL is for an unsupported site.
        
        :param url: URL to attempt downloading
        :type url: str, required
        :param directory: Directory to save into
        :type directory: str, required
        :return: Whether the download completed successfully
        :rtype: bool
        """
        for extractor in self.extractors:
            if extractor.download_from_url(url, directory):
                return True
        python_print_tools.printer.color_print(f"Unsupported URL: {url}", "r")
        return False
    
    def download_from_file(self, file:str, directory:str):
        """
        Attepts to download media from URLs in a given text file.
        
        :param file: Path of file to read URLs from
        :type file: str, required
        :param directory: Directory to save into
        :type directory: str, required
        :return: Whether the download completed successfully
        :rtype: bool
        """
        try:
            # Get lines from the text file
            lines = []
            text = mm_file_tools.read_text_file(file)
            split = text.split("\n")
            for item in split:
                lines.extend(item.split("\r"))
        except AttributeError:
            return False
        # Remove whitespace and empty lines from the list of lines
        for i in range(len(lines)-1, -1, -1):
            lines[i] = re.sub(r"^\s+|\s+$", "", lines[i])
            if lines[i] == "":
                del lines[i]
        # Download URLs
        for i in range(0, len(lines)):
            print(f"[{i+1}/{len(lines)}] {lines[i]}")
            self.download_from_url(lines[i], directory)
        return True

def main():
    """
    Sets up parser for downloading images.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "URL",
        help="URL to download.",
        nargs="?",
        type=str,
        default=None)
    parser.add_argument(
        "-d",
        "--directory",
        help="Directory in which to save media.",
        nargs="?",
        type=str,
        default=str(os.getcwd()))
    parser.add_argument(
        "-i",
        "--input-file",
        metavar="FILE",
        help=("Download URLs found in FILE"),
        type=str,
        default=None)
    args = parser.parse_args()
    full_directory = abspath(args.directory)
    if not exists(full_directory):
        # Directory is invalid
        python_print_tools.printer.color_print("Invalid directory", "r")
    else:
        if args.URL is None and args.input_file is None:
            # No URLs provided
            python_print_tools.printer.color_print("Either URL or FILE containing urls is required.", "r")
            print(r"Use 'gallery-dvk --help' to get a list of all options.")
        else:
            # Download either from file or URL
            with GalleryDVK() as dvk:
                if args.input_file is None:
                    dvk.download_from_url(args.URL, full_directory)
                else:
                    dvk.download_from_file(abspath(args.input_file), full_directory)
