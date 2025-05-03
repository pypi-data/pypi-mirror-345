#!/usr/bin/env python3

import os
import tempfile
import metadata_magic.file_tools as mm_file_tools
from gallery_dvk.extractor.overflowingbra import OverflowingBra
from os.path import abspath, basename, exists, join

def test_match_url():
    """
    Tests the match_url method.
    """
    with OverflowingBra([]) as bra:
        # Test getting OverflowingBra gallery URLs
        match = bra.match_url("https://overflowingbra.com/recentuploads.htm")
        assert match["section"] == "recentuploads.htm"
        assert match["type"] == "gallery"
        match = bra.match_url("http://overflowingbra.com/results.htm?varname=1178/")
        assert match["section"] == "results.htm?varname=1178"
        assert match["type"] == "gallery"
        match = bra.match_url("www.overflowingbra.com/ding.htm?dates=2022")
        assert match["section"] == "ding.htm?dates=2022"
        assert match["type"] == "gallery"
        match = bra.match_url("http://www.overflowingbra.com/ding.htm?titlevar=o/")
        assert match["section"] == "ding.htm?titlevar=o"
        assert match["type"] == "gallery"
        # Test non-matching URL
        assert bra.match_url("blah") is None
        assert bra.match_url("http://www.overflowingbra.com/something/else") is None

def test_get_id():
    """
    Tests the get_id function.
    """
    with OverflowingBra([]) as bra:
        index = bra.get_id("https://overflowingbra.com/download.php?StoryID=1505")
        assert index == "overflowingbra-1505"
        index = bra.get_id("https://overflowingbra.com/download.php?StoryID=138/")
        assert index == "overflowingbra-138"
        index = bra.get_id("overflowingbra.com/download.php?StoryID=147")
        assert index == "overflowingbra-147"

def test_get_stories():
    """
    Tests the get_stories function.
    """
    with OverflowingBra([]) as bra:
        # Test getting story with no tags
        stories = bra.get_stories("ding.htm?dates=1998")
        assert len(stories) == 263
        assert stories[0]["url"] == "https://overflowingbra.com/download.php?StoryID=23"
        assert stories[0]["title"] == "Air Spirits"
        assert stories[0]["author"] == "Happyguy"
        assert stories[0]["date"] == "1998-02-01"
        assert stories[0]["tags"] is None
        summary = "Happyguy says: This one is inflation, and it's a little more "\
                + "experimental; I was playing with the Gothic/Romance novel sort of... "\
                + "wait, that's just bullshit. Maybe it's just a bad story."
        assert stories[0]["summary"] == summary
        assert stories[0]["downloads"] > 6500
        assert stories[0]["downloads"] < 7000
        assert stories[0]["id"] == "23"
        # Test getting story with no description
        assert stories[3]["url"] == "https://overflowingbra.com/download.php?StoryID=294"
        assert stories[3]["title"] == "Jehana"
        assert stories[3]["author"] == "PBC"
        assert stories[3]["date"] == "1998-02-01"
        assert stories[3]["tags"] is None
        assert stories[3]["summary"] is None
        assert stories[3]["downloads"] > 8500
        assert stories[3]["downloads"] < 9500
        assert stories[3]["id"] == "294"
        # With getting story with tags
        assert stories[4]["url"] == "https://overflowingbra.com/download.php?StoryID=108"
        assert stories[4]["title"] == "Blue Milk"
        assert stories[4]["author"] == "Bad Irving"
        assert stories[4]["date"] == "1998-02-03"
        assert stories[4]["tags"] == ["Realistic Breast Size", "Chemical", "Lactation",
                "Slow Growth", "Male-to-Female"]
        summary = "\"\"The ultimate aphrodisiac\"\" is how this odd milk is marketed - "\
                + "but it's so much more than that. It's all part of an insidious plan to "\
                + "take over the world!"
        assert stories[4]["summary"] == summary
        assert stories[4]["downloads"] > 19500
        assert stories[4]["downloads"] < 20000
        assert stories[4]["id"] == "108"
        # Test getting story with no date
        stories = bra.get_stories("ding.htm?dates=2000")
        assert len(stories) == 113
        assert stories[0]["url"] == "https://overflowingbra.com/download.php?StoryID=1505"
        assert stories[0]["title"] == "The Spy Who Got Me"
        assert stories[0]["author"] == "Big Boob Spy 007"
        assert stories[0]["date"] is None
        assert stories[0]["tags"] == ["Bondage", "Chemical", "Fast Growth", "Hair Growth",
                "Unrealistic Breast Size", "Hypnosis", "Non-Consensual", "Male-to-Female",
                "Asleep Subject"]
        summary = "A unsuspecting guy brings home a big tited women from the club. "\
                + "Little does he know she has has other plans for him then sex."
        assert stories[0]["summary"] == summary
        assert stories[0]["downloads"] > 11200
        assert stories[0]["downloads"] < 11800
        assert stories[0]["id"] == "1505"
        # Test getting story with no summary or tags
        assert stories[12]["url"] == "https://overflowingbra.com/download.php?StoryID=315"
        assert stories[12]["title"] == "Lanky Lulu"
        assert stories[12]["author"] == "Axolotl"
        assert stories[12]["date"] == "2000-01-10"
        assert stories[12]["tags"] is None
        assert stories[12]["summary"] is None
        assert stories[12]["downloads"] > 8200
        assert stories[12]["downloads"] < 8700
        assert stories[12]["id"] == "315"
        # Test getting a more recent story
        stories = bra.get_stories("ding.htm?dates=2016")
        assert len(stories) == 49
        assert stories[0]["url"] == "https://overflowingbra.com/download.php?StoryID=3197"
        assert stories[0]["title"] == "Bree's ID Card Curse: Part 1"
        assert stories[0]["author"] == "superdutz"
        assert stories[0]["date"] == "2016-01-03"
        assert stories[0]["tags"] == ["Realistic Breast Size", "Instant Growth", "Magic",
                "Mental Transformation", "Non-Consensual"]
        summary = "Spiritual Successor to The ID Card. Bree's new campus ID card changes her "\
                + "into whatever is said about her. When the changes take her to a rowdy frat "\
                + "party, what will she leave like...?"
        assert stories[0]["summary"] == summary
        assert stories[0]["downloads"] > 3000
        assert stories[0]["downloads"] < 4000
        assert stories[0]["id"] == "3197"
        # Test non-gallery page
        assert bra.get_stories("storyratings.htm?rateID=2888") == []
        assert bra.get_stories("search.htm") == []
        assert bra.get_stories("author.htm") == []

def test_download_page():
    """
    Tests the download_page method.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test if ID is already in the database
        config_file = abspath(join(temp_dir, "config.json"))
        archive_file = abspath(join(temp_dir, "archive.db"))
        config = {"overflowingbra":{"archive":archive_file, "metadata":True}}
        mm_file_tools.write_json_file(config_file, config)
        with OverflowingBra([config_file]) as bra:
            bra.initialize()
            json = {"title":"Pillow Talk"}
            json["author"] = "Plato Voltaire"
            json["url"] = "https://overflowingbra.com/download.php?StoryID=412"
            bra.add_to_archive("overflowingbra-412")
            media_file = bra.download_page(json, temp_dir)
            assert media_file is None
        assert sorted(os.listdir(temp_dir)) == ["archive.db", "config.json"]
        # Test ZIP containing a single file
        with OverflowingBra([config_file]) as bra:
            bra.initialize()
            json = {"title":"Starfall"}
            json["author"] = "Plato Voltaire"
            json["url"] = "https://overflowingbra.com/download.php?StoryID=559"
            json["date"] = "1998-02-18"
            json["id"] = "559"
            media_file = bra.download_page(json, temp_dir)
            assert basename(media_file) == "Starfall.htm"
            assert exists(media_file)
        parent_folder = abspath(join(temp_dir, "OverflowingBra"))
        author_folder = abspath(join(parent_folder, "Plato Voltaire"))
        assert exists(author_folder)
        json_file = abspath(join(author_folder, "Starfall.json"))
        assert exists(json_file)
        assert sorted(os.listdir(author_folder)) == ["Starfall.htm", "Starfall.json"]
        meta = mm_file_tools.read_json_file(json_file)
        assert meta["title"] == "Starfall"
        assert meta["author"] == "Plato Voltaire"
        assert meta["url"] == "https://overflowingbra.com/download.php?StoryID=559"
        assert meta["date"] == "1998-02-18"
        assert meta["id"] == "559"
        contents = mm_file_tools.read_text_file(media_file)
        assert contents.startswith("<!Starfall>")
        assert "Quinn was drumming her fingers on the desk." in contents
        assert "Derek was all too willing to find out." in contents
        assert os.stat(media_file).st_size == 35574
        # Test ZIP containing multiple files
        with OverflowingBra([config_file]) as bra:
            bra.initialize()
            json = {"title":"Four of a Kind"}
            json["author"] = "Oppailolicus"
            json["url"] = "https://overflowingbra.com/download.php?StoryID=2877"
            json["date"] = "2013-12-31"
            json["id"] = "2877"
            media_file = bra.download_page(json, temp_dir)
            assert basename(media_file) == "Four of a Kind.zip"
            assert exists(media_file)
        parent_folder = abspath(join(temp_dir, "OverflowingBra"))
        author_folder = abspath(join(parent_folder, "Oppailolicus"))
        assert exists(author_folder)
        json_file = abspath(join(author_folder, "Four of a Kind.json"))
        assert exists(json_file)
        assert sorted(os.listdir(author_folder)) == ["Four of a Kind.json", "Four of a Kind.zip"]
        meta = mm_file_tools.read_json_file(json_file)
        assert meta["title"] == "Four of a Kind"
        assert meta["author"] == "Oppailolicus"
        assert meta["url"] == "https://overflowingbra.com/download.php?StoryID=2877"
        assert meta["date"] == "2013-12-31"
        assert meta["id"] == "2877"
        assert os.stat(media_file).st_size == 30914
        # Test that IDs have been written to the database
        with OverflowingBra([config_file]) as bra:
            bra.initialize()
            assert bra.archive_contains("overflowingbra-412")
            assert bra.archive_contains("overflowingbra-559")
            assert bra.archive_contains("overflowingbra-2877")
            assert not bra.archive_contains("overflowingbra-1234")

