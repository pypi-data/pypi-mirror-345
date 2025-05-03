#!/usr/bin/env python3

import os
import tempfile
import metadata_magic.file_tools as mm_file_tools
from gallery_dvk.gallery_dvk import GalleryDVK
from gallery_dvk.test.extractor.dummy_extractor import DummyExtractor
from os.path import abspath, join

def test_download_from_url():
    """
    Tests the download_from_url method.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with GalleryDVK() as dvk:
            # Test downloading from a supported URL
            dvk.extractors.insert(0, DummyExtractor([]))
            assert dvk.download_from_url("https://www.pythonscraping.com/img/gifts/img3.jpg", temp_dir)
            assert os.listdir(temp_dir) == ["Test Title!.jpg"]
            assert os.stat(abspath(join(temp_dir, "Test Title!.jpg"))).st_size == 71638
            # Test downloading from an unsupported URL
            assert not dvk.download_from_url("Not Applicable", temp_dir)
            assert not dvk.download_from_url("google.com/whatever", temp_dir)

def test_download_from_file():
    """
    Tests the download_from_file method.
    """
    # Create text file with list of URLs
    text = "     https://www.pythonscraping.com/img/gifts/img3.jpg \r "\
            +"https://www.pythonscraping.com/img/gifts/img2.jpg \n \n"\
            +"https://www.pythonscraping.com/img/gifts/img1.jpg  \n"\
            +"Invalid\r\n\n\r"\
            +"[URL]"
    with tempfile.TemporaryDirectory() as temp_dir:
        text_file = abspath(join(temp_dir, "links.txt"))
        mm_file_tools.write_text_file(text_file, text)
        # Attempt to download files from a list of urls in a text file
        with GalleryDVK() as dvk:
            dvk.extractors.insert(0, DummyExtractor([]))
            assert dvk.download_from_file(text_file, temp_dir)
            assert sorted(os.listdir(temp_dir)) == ["Test Title!-2.jpg", "Test Title!-3.jpg", "Test Title!.jpg", "links.txt"]
            assert os.stat(abspath(join(temp_dir, "Test Title!.jpg"))).st_size == 71638
            assert os.stat(abspath(join(temp_dir, "Test Title!-2.jpg"))).st_size == 58424
            assert os.stat(abspath(join(temp_dir, "Test Title!-3.jpg"))).st_size == 84202
    # Test downloading from invalid file
    with tempfile.TemporaryDirectory() as temp_dir:
        directory = abspath(join(temp_dir, "directory"))
        os.mkdir(directory)
        with GalleryDVK() as dvk:
            assert not dvk.download_from_file("/non/existant/file/alksdfj", temp_dir)
            assert not dvk.download_from_file(directory, temp_dir)
            assert os.listdir(temp_dir) == ["directory"]
