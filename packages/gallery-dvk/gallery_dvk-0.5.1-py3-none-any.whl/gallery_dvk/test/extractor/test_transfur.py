#!/usr/bin/env python3

import os
import tempfile
import metadata_magic.file_tools as mm_file_tools
from gallery_dvk.extractor.transfur import Transfur
from os.path import abspath, basename, exists, join

def test_match_url():
    """
    Tests the match_url method.
    """
    with Transfur([]) as transfur:
        # Test getting transfur user URL
        match = transfur.match_url("https://www.transfur.com/Users/non-existant/")
        assert match["section"] == "non-existant"
        assert match["type"] == "user"
        match = transfur.match_url("http://www.transfur.com/users/artist")
        assert match["section"] == "artist"
        assert match["type"] == "user"
        match = transfur.match_url("transfur.com/Users/Person")
        assert match["section"] == "person"
        assert match["type"] == "user"
        match = transfur.match_url("https://transfur.com/users/thing/")
        assert match["section"] == "thing"
        assert match["type"] == "user"
        # Test getting transfur gallery URL
        match = transfur.match_url("https://www.transfur.com/Users/non-existant/gallery")
        assert match["section"] == "non-existant"
        assert match["type"] == "gallery"
        match = transfur.match_url("http://www.transfur.com/users/artist/Gallery/2")
        assert match["section"] == "artist"
        assert match["type"] == "gallery"
        match = transfur.match_url("transfur.com/Users/Person/Gallery/")
        assert match["section"] == "person"
        assert match["type"] == "gallery"
        match = transfur.match_url("https://transfur.com/users/thing/gallery/5/")
        assert match["section"] == "thing"
        assert match["type"] == "gallery"
        # Test getting transfur sketch URL
        match = transfur.match_url("https://www.transfur.com/Users/non-existant/sketches")
        assert match["section"] == "non-existant"
        assert match["type"] == "sketches"
        match = transfur.match_url("http://www.transfur.com/users/artist/Sketches/2")
        assert match["section"] == "artist"
        assert match["type"] == "sketches"
        match = transfur.match_url("transfur.com/Users/Person/Sketches/")
        assert match["section"] == "person"
        assert match["type"] == "sketches"
        match = transfur.match_url("https://transfur.com/users/thing/sketches/5/")
        assert match["section"] == "thing"
        assert match["type"] == "sketches"
        # Test getting transfur favorite URL
        match = transfur.match_url("https://www.transfur.com/Users/non-existant/favorites")
        assert match["section"] == "non-existant"
        assert match["type"] == "favorites"
        match = transfur.match_url("http://www.transfur.com/users/artist/Favorites/2")
        assert match["section"] == "artist"
        assert match["type"] == "favorites"
        match = transfur.match_url("transfur.com/Users/Person/Favorites/")
        assert match["section"] == "person"
        assert match["type"] == "favorites"
        match = transfur.match_url("https://transfur.com/users/thing/favorites/5/")
        assert match["section"] == "thing"
        assert match["type"] == "favorites"
        # Test getting transfur tags URL
        match = transfur.match_url("https://www.transfur.com/Tags/other")
        assert match["section"] == "other"
        assert match["type"] == "tag"
        match = transfur.match_url("http://www.transfur.com/tags/name/2")
        assert match["section"] == "name"
        assert match["type"] == "tag"
        match = transfur.match_url("transfur.com/Tags/TagName/")
        assert match["section"] == "tagname"
        assert match["type"] == "tag"
        match = transfur.match_url("https://transfur.com/tags/thing/4/")
        assert match["section"] == "thing"
        assert match["type"] == "tag"
        # Test getting submission submission URL
        match = transfur.match_url("http://www.transfur.com/Users/Someone/Submissions/12345")
        assert match["section"] == "someone/submissions/12345"
        assert match["type"] == "submission"
        match = transfur.match_url("https://www.transfur.com/Users/Someone/Submissions/234/")
        assert match["section"] == "someone/submissions/234"
        assert match["type"] == "submission"   
        match = transfur.match_url("transfur.com/Users/thing/Submissions/987")
        assert match["section"] == "thing/submissions/987"
        assert match["type"] == "submission"
        match = transfur.match_url("http://transfur.com/Users/Person/Submissions/105")
        assert match["section"] == "person/submissions/105"
        assert match["type"] == "submission"

def test_get_id():
    """
    Tests the get_id function.
    """
    with Transfur([]) as transfur:
        index = transfur.get_id("https://transfur.com/Users/Oter/Submissions/17614")
        assert index == "transfur-oter-17614-1"
        index = transfur.get_id("www.transfur.com/Users/mxmaramoose/Submissions/27317/02")
        assert index == "transfur-mxmaramoose-27317-2"
        index = transfur.get_id("transfur.com/Users/mxmaramoose/Submissions/027317/37/")
        assert index == "transfur-mxmaramoose-27317-37"

def test_archive_contains_all():
    """
    Tests the archive_contains_all method.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = abspath(join(temp_dir, "config.json"))
        archive_file = abspath(join(temp_dir, "tf.sqlite3"))
        config = {"transfur":{"archive":archive_file}}
        mm_file_tools.write_json_file(config_file, config)
        assert exists(config_file)
        base = "https://www.transfur.com/Users/"
        with Transfur([config_file]) as transfur:
            # Test if the database contains the main page
            transfur.initialize()
            transfur.add_to_archive("transfur-nonexist-8080-1")
            assert transfur.archive_contains("transfur-nonexist-8080-1")
            assert transfur.archive_contains_all(f"{base}nonexist/Submissions/8080", 1)
            assert not transfur.archive_contains_all(f"{base}nonexist/Submissions/1234", 1)
            # Test if database only contains some of the images in a sequence
            transfur.add_to_archive("transfur-nonexist-5000-1")
            transfur.add_to_archive("transfur-nonexist-5000-2")
            transfur.add_to_archive("transfur-nonexist-5000-3")
            transfur.add_to_archive("transfur-nonexist-40-2")
            transfur.add_to_archive("transfur-nonexist-24-1")
            transfur.add_to_archive("transfur-nonexist-24-2")
            assert transfur.archive_contains_all(f"{base}nonexist/Submissions/5000/2", 3)
            assert not transfur.archive_contains_all(f"{base}nonexist/Submissions/8080", 2)
            assert not transfur.archive_contains_all(f"{base}nonexist/Submissions/40/2", 3)
            assert not transfur.archive_contains_all(f"{base}nonexist/Submissions/24", 3)

def test_get_info_from_page():
    """
    Tests the get_info_from_page method.
    """
    base = "https://www.transfur.com/users/"
    with Transfur([]) as transfur:
        # Test getting page with single image
        pages = transfur.get_info_from_page("Oter/Submissions/17614")
        assert len(pages) == 1
        assert pages[0]["title"] == "Bear TF TG"
        assert pages[0]["artist"] == "Oter"
        assert pages[0]["date"] == "2013-12-13"
        assert pages[0]["url"] == f"{base}oter/submissions/17614"
        assert pages[0]["image_url"] == f"{base}oter/images/bear%20tf%20tg%20final.jpg"
        assert pages[0]["tags"] == ["Bear", "Gender Change", "Gender Change - Male to Female", "Surprised"]
        assert pages[0]["views"] is None
        assert pages[0]["favorites"] > 114
        assert pages[0]["favorites"] < 120
        assert pages[0]["description"] == "<p>Auction piece for Truttle on FA.</p>"
        assert pages[0]["image_number"] == 1
        assert pages[0]["total_images"] == 1
        assert pages[0]["id"] == "17614-1"
        # Test getting page with multiple images
        pages = transfur.get_info_from_page("mxmaramoose/submissions/27317")
        assert len(pages) == 3
        assert pages[0]["title"] == "Unexpected Happiness"
        assert pages[0]["artist"] == "Mxmaramoose"
        assert pages[0]["date"] == "2022-08-25"
        assert pages[0]["tags"] == ["Fox", "Gender Change - Male to Female", "Happy", "Surprised"]
        assert pages[0]["views"] is None
        assert pages[0]["favorites"] > 45
        assert pages[0]["favorites"] < 55
        description = "<p>Sometimes life throws an unexpected boon your way..."\
                +"<a href=\"/Users/WuffKitty\">WuffKitty</a> certainly isn't gonna "\
                +"question their sudden transformation ^^ #TFEveryday</p>"
        assert pages[0]["description"] == description
        assert pages[0]["url"] == f"{base}mxmaramoose/submissions/27317/1"
        assert pages[0]["image_url"] == f"{base}mxmaramoose/images/lily%20full.png"
        assert pages[0]["id"] == "27317-1"
        assert pages[0]["image_number"] == 1
        assert pages[0]["total_images"] == 3
        assert pages[1]["title"] == "Unexpected Happiness"
        assert pages[1]["artist"] == "Mxmaramoose"
        assert pages[1]["url"] == f"{base}mxmaramoose/submissions/27317/2"
        assert pages[1]["image_url"] == f"{base}mxmaramoose/images/lily%20screensaver1.png"
        assert pages[1]["image_number"] == 2
        assert pages[1]["id"] == "27317-2"
        assert pages[2]["title"] == "Unexpected Happiness"
        assert pages[2]["artist"] == "Mxmaramoose"
        assert pages[2]["url"] == f"{base}mxmaramoose/submissions/27317/3"
        assert pages[2]["image_url"] == f"{base}mxmaramoose/images/lily%20screensaver2.png"
        assert pages[2]["image_number"] == 3
        assert pages[2]["id"] == "27317-3"
        # Test trying to get mature content when not logged in
        assert transfur.get_info_from_page("Danwolf/Submissions/26719") == []

def test_get_links_from_gallery():
    """
    Tests the get_links_from_gallery method.
    """
    # Test getting links from gallery with only one page
    base = "https://www.transfur.com/Users/"
    with Transfur([]) as transfur:
        links = transfur.get_links_from_gallery(f"{base}danwolf/Sketches")
        assert len(links) == 1
        assert links[0] == {"section":"danwolf/submissions/20035", "num_images":5}
    # Test getting links from gallery with no pages
    with Transfur([]) as transfur:
        links = transfur.get_links_from_gallery(f"{base}strawberrytfs/Sketches")
        assert len(links) == 0
    # Test getting links from gallery with many pages
    with Transfur([]) as transfur:
        links = transfur.get_links_from_gallery(f"{base}picklejuice/Gallery")
        assert len(links) > 150
        assert {"section":"picklejuice/submissions/25658", "num_images":1} in links
        assert {"section":"picklejuice/submissions/23039", "num_images":1} in links
        assert {"section":"picklejuice/submissions/21284", "num_images":3} in links
        assert {"section":"picklejuice/submissions/21302", "num_images":22} in links
        assert {"section":"picklejuice/submissions/17398", "num_images":1} in links
        assert {"section":"picklejuice/submissions/9104", "num_images":3} in links
        assert {"section":"picklejuice/submissions/426", "num_images":10} in links
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test not getting already downloaded links
        config_file = abspath(join(temp_dir, "config.json"))
        archive_file = abspath(join(temp_dir, "transfur.db"))
        config = {"transfur":{"archive":archive_file, "metadata":True}}
        mm_file_tools.write_json_file(config_file, config)
        with Transfur([config_file]) as transfur:
            transfur.initialize()
            transfur.add_to_archive("transfur-angrboda-11122-1")
            transfur.add_to_archive("transfur-angrboda-11122-2")
            transfur.add_to_archive("transfur-angrboda-11122-3")
            transfur.add_to_archive("transfur-angrboda-11122-4")
            transfur.add_to_archive("transfur-angrboda-7491-1")
            transfur.add_to_archive("transfur-angrboda-8985-1")
            transfur.add_to_archive("transfur-angrboda-10765-2")
            transfur.add_to_archive("transfur-angrboda-10765-3")
            links = transfur.get_links_from_gallery(f"{base}angrboda/Gallery")
            assert not {"section":"angrboda/submissions/7491", "num_images":1} in links
            assert not {"section":"angrboda/submissions/11122", "num_images":4} in links
            assert {"section":f"angrboda/submissions/8985", "num_images":3} in links
            assert {"section":f"angrboda/submissions/10765", "num_images":4} in links
            assert {"section":f"angrboda/submissions/8744", "num_images":1} in links
            assert {"section":f"angrboda/submissions/7003", "num_images":8} in links
            assert {"section":f"angrboda/submissions/3030", "num_images":1} in links
            assert {"section":f"angrboda/submissions/3018", "num_images":1} in links

def test_download_page():
    """
    Tests the download_page method.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test if ID is already in the database
        base = "https://www.transfur.com/Users/"
        config_file = abspath(join(temp_dir, "config.json"))
        archive_file = abspath(join(temp_dir, "transfur.db"))
        config = {"transfur":{"archive":archive_file, "metadata":True}}
        mm_file_tools.write_json_file(config_file, config)
        with Transfur([config_file]) as transfur:
            transfur.initialize()
            json = {"title":"Unexpected Happiness"}
            json["url"] = f"{base}mxmaramoose/Submissions/27317/2"
            json["artist"] = "Mxmaramoose"
            transfur.add_to_archive("transfur-mxmaramoose-27317-2")
            media_file = transfur.download_page(json, temp_dir)
            assert media_file is None
        files = sorted(os.listdir(temp_dir)) == ["config.json", "transfur.db"]
        # Test if file has not been written
        with Transfur([config_file]) as transfur:
            json = {"title":"Bear TF TG"}
            json["id"] = "17614-1"
            json["artist"] = "Oter"
            json["url"] = f"{base}Oter/Submissions/17614"
            json["image_url"] = f"{base}oter/Images/bear%20tf%20tg%20final.jpg"
            media_file = transfur.download_page(json, temp_dir)
            assert basename(media_file) == "17614-1_Bear TF TG.jpg"
            assert exists(media_file)
        parent_folder = abspath(join(temp_dir, "Transfur"))
        artist_folder = abspath(join(parent_folder, "Oter"))
        assert exists(artist_folder)
        json_file = abspath(join(artist_folder, "17614-1_Bear TF TG.json"))
        assert exists(json_file)
        meta = mm_file_tools.read_json_file(json_file)
        assert meta["title"] == "Bear TF TG"
        assert meta["artist"] == "Oter"
        assert meta["url"] == f"{base}Oter/Submissions/17614"
        assert meta["image_url"] == f"{base}oter/Images/bear%20tf%20tg%20final.jpg"
        assert os.stat(media_file).st_size == 261987
        # Test that ID has been written to the database
        with Transfur([config_file]) as transfur:
            transfur.initialize()
            assert transfur.archive_contains("transfur-mxmaramoose-27317-2")
            assert transfur.archive_contains("transfur-oter-17614-1")
            assert not transfur.archive_contains("transfur-nonexist-12345")

def test_with_login():
    """
    Tests getting info from Transfur pages that are unavailable when not logged in.
    Requires a user config file with Transfur username and password to pass.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        archive_file = abspath(join(temp_dir, "transfur.db"))
        with Transfur() as transfur:
            # Nullify archive_file so user archive isn't overwritten
            try:
                transfur.archive_connection.close()
            except AttributeError: pass
            transfur.filename_format = "{id}_{title}"
            transfur.archive_file = archive_file
            transfur.open_archive()
            transfur.write_metadata = True
            # Test logging in
            if transfur.username is None or transfur.password is None:
                raise Exception("Transfur Username and Password must be provided in a user config file to perform this test.")
            assert transfur.login(transfur.username, transfur.password)
            assert transfur.attempted_login
            # Test getting links from gallery that are not shown unless logged in
            base = "https://www.transfur.com/users/"
            links = transfur.get_links_from_gallery(f"{base}danwolf/Gallery")
            assert {"section":"danwolf/submissions/27823", "num_images":1} in links
            assert {"section":"danwolf/submissions/26904", "num_images":1} in links
            assert {"section":"danwolf/submissions/25295", "num_images":1} in links
            # Test getting info from page that is locked when not logged in
            pages = transfur.get_info_from_page("Danwolf/Submissions/26719")
            assert len(pages) == 1
            assert pages[0]["title"] == "Digimon beast"
            assert pages[0]["artist"] == "Danwolf"
            assert pages[0]["date"] == "2021-05-01"
            assert pages[0]["url"] == f"{base}danwolf/submissions/26719"
            assert pages[0]["image_url"] == f"{base}danwolf/images/resizerimage1280x1810.jpg"
            assert pages[0]["tags"] == ["Big", "Digimon", "Muscular", "Shapeshifter",
                    "Traditional", "Werecreature", "Weregarurumon", "Wolf"]
            assert pages[0]["views"] is None
            assert pages[0]["favorites"] > 25
            assert pages[0]["favorites"] < 35
            description = "<p>Foxlightning wanted his a beefy version of his favorite boi ! "\
                    +"Wish granted &gt;:3</p>"
            assert pages[0]["description"] == description
            assert pages[0]["image_number"] == 1
            assert pages[0]["total_images"] == 1
            assert pages[0]["id"] == "26719-1"
            # Test downloading page that is locked when not logged in
            json = {"title":"Digimon beast"}
            json["id"] = "26719-1"
            json["artist"] = "Danwolf"
            json["url"] = f"{base}danwolf/submissions/26719"
            json["image_url"] = f"{base}danwolf/images/resizerimage1280x1810.jpg"
            media_file = transfur.download_page(json, temp_dir)
            assert basename(media_file) == "26719-1_Digimon beast.jpg"
            assert exists(media_file)
            parent_folder = abspath(join(temp_dir, "Transfur"))
            artist_folder = abspath(join(parent_folder, "Danwolf"))
            assert exists(artist_folder)
            json_file = abspath(join(artist_folder, "26719-1_Digimon beast.json"))
            assert exists(json_file)
            meta = mm_file_tools.read_json_file(json_file)
            assert meta["title"] == "Digimon beast"
            assert meta["artist"] == "Danwolf"
            assert meta["url"] == f"{base}danwolf/submissions/26719"
            assert meta["image_url"] == f"{base}danwolf/images/resizerimage1280x1810.jpg"
            assert os.stat(media_file).st_size == 249183
