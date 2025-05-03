#!/usr/bin/env python3

import os
import tempfile
import metadata_magic.file_tools as mm_file_tools
from gallery_dvk.extractor.docslab import DocsLab
from os.path import abspath, basename, exists, join

def test_match_url():
    """
    Tests the match_url function.
    """
    with DocsLab([]) as docslab:
        # Test getting docslab user URL
        match = docslab.match_url("https://www.docs-lab.com/Profiles/non-existant/")
        assert match["section"] == "non-existant"
        assert match["type"] == "user"
        match = docslab.match_url("http://www.docs-lab.com/profiles/artist")
        assert match["section"] == "artist"
        assert match["type"] == "user"
        match = docslab.match_url("docs-lab.com/profiles/Person")
        assert match["section"] == "person"
        assert match["type"] == "user"
        match = docslab.match_url("http://docs-lab.com/profiles/thing/")
        assert match["section"] == "thing"
        assert match["type"] == "user"
        # Test getting docslab submission URL
        match = docslab.match_url("http://docs-lab.com/submissions/1234/test-thing")
        assert match["section"] == "1234/test-thing"
        assert match["type"] == "submission"
        match = docslab.match_url("https://www.docs-lab.com/submissions/5678/Other/")
        assert match["section"] == "5678/other"
        assert match["type"] == "submission"   
        match = docslab.match_url("docs-lab.com/submissions/4545/thing")
        assert match["section"] == "4545/thing"
        assert match["type"] == "submission"
        match = docslab.match_url("http://docs-lab.com/submissions/9876/New/")
        assert match["section"] == "9876/new"
        assert match["type"] == "submission"

def test_get_id():
    """
    Tests the get_id method.
    """
    with DocsLab([]) as docslab:
        assert docslab.get_id("http://www.docs-lab.com/submissions/1234/test-thing") == "docslab-1234"
        assert docslab.get_id("docs-lab.com/submissions/45678/test/") == "docslab-45678"
        assert docslab.get_id("www.docs-lab.com/submissions/37/other/") == "docslab-37"
        assert docslab.get_id("https://docs-lab.com/submissions/987/new") == "docslab-987"

def test_get_info_from_config():
    """
    Tests the get_info_from_config method.
    """
    # Test if there is no config file to get info from
    with DocsLab([]) as docslab:
        assert docslab.archive_file is None
        assert docslab.archive_connection is None
        assert not docslab.write_metadata
        assert not docslab.download_stories
        assert not docslab.download_artwork
    # Test getting the archive_file from the config file
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = abspath(join(temp_dir, "config.json"))
        config = {"docslab":{"archive":"/file/path/"}, "other":{"archive":"thing"}}
        mm_file_tools.write_json_file(config_file, config)
        assert exists(config_file)
        with DocsLab([config_file]) as docslab:
            assert docslab.archive_file == "/file/path/"
            assert docslab.archive_connection is None
            assert not docslab.write_metadata
        # Test getting the download_stories variable
        config = {"docslab":{"download_stories":True}, "other":{"metadata":False}}
        mm_file_tools.write_json_file(config_file, config)
        with DocsLab([config_file]) as docslab:
            assert docslab.download_stories
        # Test getting the download_artwork variable
        config = {"docslab":{"download_artwork":True}, "other":{"metadata":False}}
        mm_file_tools.write_json_file(config_file, config)
        with DocsLab([config_file]) as docslab:
            assert docslab.download_artwork

def test_get_submission_info():
    """
    Tests the get_submission_info function.
    """
    # Get story submission with rating provided
    with DocsLab([]) as docslab:
        page = docslab.get_submission_info("3339/solo-play-ch-01", "FakeRating")
        assert page["id"] == "3339"
        assert page["url"] == "https://www.docs-lab.com/submissions/3339/solo-play-ch-01"
        assert page["title"] == "Solo Play Ch. 01"
        assert page["artist"] == "lycandope"
        assert page["date"] == "2021-10-02"
        assert page["last_edit"] == "2021-10-02"
        assert len(page["tags"]) == 3
        assert page["tags"] == ["transformation", "masturbation", "doggirl"]
        assert page["age_rating"] == "FakeRating"
        assert page["user_rating"] > 90 and page["user_rating"] < 100
        assert page["favorites"] > 17
        assert page["favorites"] < 25
        assert page["description"] == "A young woman enjoys some time alone with her curse."
        assert page["text"].startswith("<!DOCTYPE html><html><body><p>\"No, I love")
        assert "It started with her heartbeat," in page["text"]
        assert "<em>Soon.</em>" in page["text"]
        assert page["text"].endswith("</p></body></html>")
        assert page["image_url"] is None
        assert page["story_link"] is None
        assert page["art_link"] is None
        assert page["type"] == "story"
    # Get image submission
    with DocsLab([]) as docslab:
        page = docslab.get_submission_info("4657/new-zoo-geese")
        assert page["id"] == "4657"
        assert page["url"] == "https://www.docs-lab.com/submissions/4657/new-zoo-geese"
        assert page["title"] == "New Zoo-Geese"
        assert page["artist"] == "wallace111"
        assert page["date"] == "2023-08-02"
        assert page["last_edit"] == "2023-08-02"
        assert page["tags"] == []
        assert page["age_rating"] == "R"
        assert page["user_rating"] > 50 and page["user_rating"] < 70
        assert page["favorites"] == 0
        assert page["description"] is None
        assert page["image_url"] == "https://www.docs-lab.com/img/art/3886_1691011708.png"
        assert page["text"] is None
        assert page["story_link"] == "https://www.docs-lab.com/submissions/2574/new-zoo-geese"
        assert page["art_link"] is None
        assert page["type"] == "art"
    # Get story with image submission
    with DocsLab([]) as docslab:
        page = docslab.get_submission_info("2574/new-zoo-geese")
        assert page["id"] == "2574"
        assert page["url"] == "https://www.docs-lab.com/submissions/2574/new-zoo-geese"
        assert page["title"] == "New Zoo-Geese"
        assert page["artist"] == "wallace111"
        assert page["date"] == "2020-09-26"
        assert page["last_edit"] == "2023-08-19"
        assert page["tags"] == ["people to geese", "mating", "goose",
                    "animal transformation", "bird", "part of series", "geese", "zoo"]
        assert page["age_rating"] == "R"
        assert page["user_rating"] > 60 and page["user_rating"] < 80
        assert page["favorites"] > 1 and page["favorites"] < 5
        desc = "A Family heads to the New Zoo to spend one last time together. Due to "\
                    +"extreme circumstances, this time winds up being much longer than "\
                    +"they could possibly anticipate.<br/><br/>Loosely inspired by "\
                    +"Aranias 'New Zoo' Tf artwork<br/><br/>Support the original source "\
                    +"at arania.kamiki.net<br/><br/>Feel Free to Comment"
        assert page["description"] == desc
        assert page["image_url"] is None
        assert "A family walked under the stone archways of the" in page["text"]
        assert "“HONK!” honked Linda," in page["text"]
        assert "The Zoo's Future. The Manager's Future...Their Future." in page["text"]
        assert page["story_link"] is None
        assert page["art_link"] == "https://www.docs-lab.com/submissions/4657/new-zoo-geese"
        assert page["type"] == "story"
    # Test getting info from an invalid page
    with DocsLab([]) as docslab:
        assert docslab.get_submission_info("3128/nola-day-2") is None

def test_get_links_from_user():
    """
    Tests the get_links_from_user method.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = abspath(join(temp_dir, "config.json"))
        archive_file = abspath(join(temp_dir, "docslab.db"))
        config = {"docslab":{"archive":archive_file, "metadata":True}}
        mm_file_tools.write_json_file(config_file, config)
        with DocsLab([config_file]) as docslab:
            # Test getting submissions
            links = docslab.get_links_from_user("lycandope", get_submissions=True, get_favorites=False)
            assert len(links) > 75
            assert len(links) < 85
            assert {"section":"3637/a-close-companion", "rating":"R"} in links
            assert {"section":"2917/comfort", "rating":"PG"} in links
            assert {"section":"2862/the-gift-ch-01", "rating":"X"} in links
            assert {"section":"3474/what-goes-around", "rating":"X"} in links
            # Test getting favorites
            links = docslab.get_links_from_user("gabrielmoon", get_submissions=False, get_favorites=True)
            assert len(links) > 15
            assert len(links) < 20
            assert {"section":"2011/assembly-for-animals", "rating":None} in links
            assert {"section":"2096/so-you-want-to-be-a-zebra", "rating":None} in links
            assert {"section":"176/stud-mare", "rating":None} in links
            assert {"section":"1649/you-and-your-beef", "rating":None} in links
            # Test getting favorites
            links = docslab.get_links_from_user("gabrielmoon", get_submissions=True, get_favorites=True)
            assert len(links) > 300
            assert len(links) < 340
            assert {"section":"2011/assembly-for-animals", "rating":None} in links
            assert {"section":"2096/so-you-want-to-be-a-zebra", "rating":None} in links
            assert {"section":"176/stud-mare", "rating":None} in links
            assert {"section":"1649/you-and-your-beef", "rating":None} in links
            assert {"section":"3006/a-canadian-werewolf-in-philly", "rating":"X"} in links
            assert {"section":"4103/wooing-wilderness-and-wolves", "rating":"X"} in links
            # Test not including already downloaded files
            docslab.add_to_archive("docslab-3637")
            docslab.add_to_archive("docslab-2917")
            docslab.add_to_archive("docslab-2862")
            links = docslab.get_links_from_user("lycandope", get_submissions=True, get_favorites=False)
            assert len(links) > 65
            assert len(links) < 90
            assert {"section":"3637/a-close-companion", "rating":"R"} not in links
            assert {"section":"2917/comfort", "rating":"PG"} not in links
            assert {"section":"2862/the-gift-ch-01", "rating":"X"} not in links
            assert {"section":"3430/esssssential-oilsssss", "rating":"X"} in links
            assert {"section":"3474/what-goes-around", "rating":"X"} in links

def test_download_page():
    """
    Tests the download_page method.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test if the ID is already in the archive
        config_file = abspath(join(temp_dir, "config.json"))
        archive_file = abspath(join(temp_dir, "docslab.db"))
        config = {"docslab":{"archive":archive_file, "metadata":True}}
        mm_file_tools.write_json_file(config_file, config)
        with DocsLab([config_file]) as docslab:
            docslab.initialize()
            json = {"title":"A Party to Remember"}
            json["url"] = "https://www.docs-lab.com/submissions/3600/a-party-to-remember"
            json["artist"] = "gabrielmoon"
            json["art_link"] = None
            json["story_link"] = None
            docslab.add_to_archive("docslab-3600")
            media_file = docslab.download_page(json, temp_dir)
            assert media_file is None
        files = sorted(os.listdir(temp_dir)) == ["config.json", "docslab.db"]
        # Test downloading a story submission
        with DocsLab([config_file]) as docslab:
            json = {"title":"Reflect On That, Chess"}
            json["id"] = "2434"
            json["artist"] = "kayemarquet"
            json["url"] = "https://www.docs-lab.com/submissions/2434/reflect-on-that-chess"
            json["text"] = "<!DOCTYPE html><html>Test!</html>"
            json["art_link"] = None
            json["story_link"] = None
            media_file = docslab.download_page(json, temp_dir)
            assert basename(media_file) == "2434_Reflect On That, Chess.html"
            assert exists(media_file)
        parent_folder = abspath(join(temp_dir, "DocsLab"))
        artist_folder = abspath(join(parent_folder, "kayemarquet"))
        assert exists(artist_folder)
        json_file = abspath(join(artist_folder, "2434_Reflect On That, Chess.json"))
        assert exists(json_file)
        meta = mm_file_tools.read_json_file(json_file)
        assert meta["id"] == "2434"
        assert meta["title"] == "Reflect On That, Chess"
        assert meta["artist"] == "kayemarquet"
        assert meta["url"] == "https://www.docs-lab.com/submissions/2434/reflect-on-that-chess"
        assert mm_file_tools.read_text_file(media_file) == "<!DOCTYPE html><html>Test!</html>"
        # Test downloading a story submission with an image
        config = {"docslab":{"archive":archive_file, "metadata":True, "download_artwork":True}}
        mm_file_tools.write_json_file(config_file, config)
        with DocsLab([config_file]) as docslab:
            json = {"title":"New Zoo-Bears"}
            json["id"] = "2585"
            json["artist"] = "wallace111"
            json["url"] = "https://www.docs-lab.com/submissions/2585/new-zoo-bears"
            json["text"] = "<!DOCTYPE html><html>Other</html>"
            json["art_link"] = "https://www.docs-lab.com/submissions/4701/new-zoo-bears"
            json["story_link"] = None
            media_file = docslab.download_page(json, temp_dir)
            assert basename(media_file) == "2585_New Zoo-Bears.html"
            assert exists(media_file)
        parent_folder = abspath(join(temp_dir, "DocsLab"))
        artist_folder = abspath(join(parent_folder, "wallace111"))
        assert exists(artist_folder)
        json_file = abspath(join(artist_folder, "2585_New Zoo-Bears.json"))
        assert exists(json_file)
        meta = mm_file_tools.read_json_file(json_file)
        assert meta["id"] == "2585"
        assert meta["title"] == "New Zoo-Bears"
        assert meta["artist"] == "wallace111"
        assert meta["url"] == "https://www.docs-lab.com/submissions/2585/new-zoo-bears"
        assert meta["art_link"] == "https://www.docs-lab.com/submissions/4701/new-zoo-bears"
        assert mm_file_tools.read_text_file(media_file) == "<!DOCTYPE html><html>Other</html>"
        art_json = abspath(join(artist_folder, "4701_New Zoo-Bears.json"))
        assert exists(art_json)
        meta = mm_file_tools.read_json_file(art_json)
        assert meta["id"] == "4701"
        assert meta["title"] == "New Zoo-Bears"
        assert meta["artist"] == "wallace111"
        assert meta["url"] == "https://www.docs-lab.com/submissions/4701/new-zoo-bears"
        assert meta["image_url"] == "https://www.docs-lab.com/img/art/3886_1693141935.png"
        art_media = abspath(join(artist_folder, "4701_New Zoo-Bears.png"))
        assert exists(art_media)
        assert os.stat(art_media).st_size == 598728
        # Test downloading an image submission with a story
        config = {"docslab":{"archive":archive_file, "metadata":True, "download_stories":True}}
        mm_file_tools.write_json_file(config_file, config)
        with DocsLab([config_file]) as docslab:
            json = {"title":"New Zoo-Geese"}
            json["id"] = "4657"
            json["artist"] = "wallace111"
            json["url"] = "https://www.docs-lab.com/submissions/4657/new-zoo-geese"
            json["image_url"] = "https://www.docs-lab.com/img/art/3886_1691011708.png"
            json["story_link"] = "https://www.docs-lab.com/submissions/2574/new-zoo-geese"
            json["art_link"] = None
            media_file = docslab.download_page(json, temp_dir)
            assert basename(media_file) == "4657_New Zoo-Geese.png"
            assert exists(media_file)
        parent_folder = abspath(join(temp_dir, "DocsLab"))
        artist_folder = abspath(join(parent_folder, "wallace111"))
        assert exists(artist_folder)
        json_file = abspath(join(artist_folder, "4657_New Zoo-Geese.json"))
        assert exists(json_file)
        meta = mm_file_tools.read_json_file(json_file)
        assert meta["id"] == "4657"
        assert meta["title"] == "New Zoo-Geese"
        assert meta["artist"] == "wallace111"
        assert meta["url"] == "https://www.docs-lab.com/submissions/4657/new-zoo-geese"
        assert meta["image_url"] == "https://www.docs-lab.com/img/art/3886_1691011708.png"
        assert meta["story_link"] == "https://www.docs-lab.com/submissions/2574/new-zoo-geese"
        assert os.stat(media_file).st_size == 736493
        story_json = abspath(join(artist_folder, "2574_New Zoo-Geese.json"))
        assert exists(story_json)
        meta = mm_file_tools.read_json_file(story_json)
        assert meta["id"] == "2574"
        assert meta["title"] == "New Zoo-Geese"
        assert meta["artist"] == "wallace111"
        assert meta["url"] == "https://www.docs-lab.com/submissions/2574/new-zoo-geese"
        story_file = abspath(join(artist_folder, "2574_New Zoo-Geese.html"))
        assert exists(story_file)
        text = mm_file_tools.read_text_file(story_file)
        assert "A family walked under the stone" in text
        # Test that submission IDs were added to the archive
        with DocsLab([config_file]) as docslab:
            docslab.initialize()
            assert docslab.archive_contains("docslab-3600")
            assert docslab.archive_contains("docslab-2434")
            assert docslab.archive_contains("docslab-2585")
            assert docslab.archive_contains("docslab-4701")
            assert docslab.archive_contains("docslab-4657")
            assert docslab.archive_contains("docslab-2574")
            assert not docslab.archive_contains("docslab-12345")
            assert not docslab.archive_contains("docslab-0245")
