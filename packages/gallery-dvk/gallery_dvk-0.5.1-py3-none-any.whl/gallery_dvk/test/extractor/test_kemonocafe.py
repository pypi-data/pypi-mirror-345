#!/usr/bin/env python3

import os
import tempfile
import metadata_magic.file_tools as mm_file_tools
from gallery_dvk.extractor.kemonocafe import KemonoCafe
from os.path import abspath, basename, exists, join

def test_match_url():
    """
    Tests the match_url method.
    """
    with KemonoCafe([]) as kemonocafe:
        # Test getting kemoko cafe comic pages
        match = kemonocafe.match_url("https://www.theeye.kemono.cafe/comic/instant-abs/")
        assert match["section"] == "theeye.kemono.cafe/comic/instant-abs"
        assert match["type"] == "comic_page"
        match = kemonocafe.match_url("Paprika.Kemono.cafe/Comic/page000")
        assert match["section"] == "paprika.kemono.cafe/comic/page000"
        assert match["type"] == "comic_page"
        match = kemonocafe.match_url("http://AddictiveScience.kemono.cafe/comic/page2404/")
        assert match["section"] == "addictivescience.kemono.cafe/comic/page2404"
        assert match["type"] == "comic_page"
        # Test getting kemoko cafe archive pages
        match = kemonocafe.match_url("https://AddictiveScience.kemono.cafe/archive/")
        assert match["section"] == "addictivescience"
        assert match["type"] == "archive"
        match = kemonocafe.match_url("Paprika.kemono.cafe/archive/")
        assert match["section"] == "paprika"
        assert match["type"] == "archive"
        match = kemonocafe.match_url("http://TheEye.kemono.cafe")
        assert match["section"] == "theeye"
        assert match["type"] == "archive"
        match = kemonocafe.match_url("https://rascals.kemono.cafe/")
        assert match["section"] == "rascals"
        assert match["type"] == "archive"

def test_get_id():
    """
    Tests the get_id function.
    """
    with KemonoCafe([]) as kemonocafe:
        index = kemonocafe.get_id("https://addictivescience.kemono.cafe/comic/page0002/")
        assert index == "kemonocafe-addictivescience-page0002"
        index = kemonocafe.get_id("theeye.kemono.cafe/comic/theeye-page245")
        assert index == "kemonocafe-theeye-theeye-page245"
        index = kemonocafe.get_id("paprika.kemono.cafe/comic/page060/")
        assert index == "kemonocafe-paprika-page060"

def test_get_comic_pages():
    """
    Tests the get_comic_pages method.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = abspath(join(temp_dir, "config.json"))
        archive_file = abspath(join(temp_dir, "kemonocafe.db"))
        config = {"kemonocafe":{"archive":archive_file, "metadata":True}}
        mm_file_tools.write_json_file(config_file, config)
        with KemonoCafe([config_file]) as kemonocafe:
            # Test getting pages
            pages = kemonocafe.get_comic_pages("paprika")
            assert len(pages) > 128
            assert "paprika.kemono.cafe/comic/page000" in pages
            assert "paprika.kemono.cafe/comic/page001" in pages
            assert "paprika.kemono.cafe/comic/page-128-shrodingers-pizza" in pages
            assert "paprika.kemono.cafe/comic/page-127-the-perfect-lifeform" in pages
            assert "paprika.kemono.cafe/comic/page128" not in pages
            # Test getting pages that have already been downloaded
            kemonocafe.initialize()
            kemonocafe.add_to_archive("kemonocafe-paprika-page000")
            kemonocafe.add_to_archive("kemonocafe-paprika-page-127-the-perfect-lifeform")
            assert kemonocafe.archive_contains("kemonocafe-paprika-page000")
            pages = kemonocafe.get_comic_pages("paprika")
            assert len(pages) > 126
            assert "paprika.kemono.cafe/comic/page001" in pages
            assert "paprika.kemono.cafe/comic/page-128-shrodingers-pizza" in pages
            assert "paprika.kemono.cafe/comic/page060" in pages
            assert "paprika.kemono.cafe/comic/page000" not in pages
            assert "paprika.kemono.cafe/comic/page-127-the-perfect-lifeform" not in pages
            assert "paprika.kemono.cafe/comic/page128" not in pages
        

def test_get_chapter_info():
    """
    Tests the get_chapter_info method.
    """
    with KemonoCafe([]) as kemonocafe:
        chapters = kemonocafe.get_chapter_info("paprika")
        assert len(chapters) == 4
        assert chapters[0]["title"] == "Paprika!"
        desc = "Welcome to Paprika, a celebration of creativity and the power of "\
                    +"imagination! Follow Tina Hachi as she attends her very first "\
                    +"anime convention and meets her lifelong friends. Be careful, "\
                    +"though Nekomimi have very powerful imaginations and if you're "\
                    +"swept up in them... there's no telling where you'll end up."
        assert chapters[0]["description"] == desc
        assert chapters[0]["date"] == "2017-01-01"
        assert chapters[0]["links"] == ["paprika.kemono.cafe/comic/page000"]
        assert chapters[1]["title"] == "Nekomimi"
        assert chapters[1]["date"] == "2017-01-20"
        assert chapters[1]["links"] == ["paprika.kemono.cafe/comic/page019"]
        assert "Now with Yuki and Ruby on her side" in chapters[1]["description"]
        assert chapters[2]["title"] == "Tiger Special"
        assert chapters[2]["date"] == "2017-03-02"
        assert chapters[2]["links"] == ["paprika.kemono.cafe/comic/page060"]
        assert "Tina can't help but" in chapters[2]["description"]
        assert chapters[3]["title"] == "Animeko"
        assert chapters[3]["date"] == "2017-04-17"
        assert chapters[3]["links"] == ["paprika.kemono.cafe/comic/page105"]
        assert "Even in small doses, the" in chapters[3]["description"]
        # Test getting chapter info for chapters with multiple links
        chapters = kemonocafe.get_chapter_info("addictivescience")
        assert len(chapters) == 49
        assert chapters[0]["title"] == "group_1"
        assert chapters[0]["date"] == "2013-01-01"
        assert chapters[0]["description"] is None
        assert len(chapters[0]["links"]) == 50
        assert "addictivescience.kemono.cafe/comic/page0001" in chapters[0]["links"]
        assert "addictivescience.kemono.cafe/comic/page0002" in chapters[0]["links"]
        assert "addictivescience.kemono.cafe/comic/page0050" in chapters[0]["links"]

def test_get_page_info():
    """
    Tests the get_page_info method.
    """
    with KemonoCafe([]) as kemonocafe:
        # Test loading a standard page
        page = kemonocafe.get_page_info("addictivescience.kemono.cafe/comic/page0002")
        assert page["id"] == "addictivescience-page0002"
        assert page["title"] == "Page0002"
        assert page["url"] == "https://addictivescience.kemono.cafe/comic/page0002/"
        assert page["image_url"] == "https://addictivescience.kemono.cafe/wp-content/uploads/sites/12/2019/09/2013-01-02-page0002.jpg"
        assert page["date"] == "2013-01-02"
        assert page["comic"] == "Addictive Science"
        assert page["tagline"] == "Addictive Science | A Science Webcomic by Cervelet"
        assert page["author"] == "KC Staff"
        assert page["chapter"] == "group_1"
        assert page["chapter_description"] is None
        assert page["post_content"] is None
        # Test loading page with description and forwarded url
        chapters = [{"links":[], "date":"2001-01-01", "title":"Not This", "description":"blah"}]
        chapters.append({"links":[], "date":"2021-01-01", "title":"Chapter Name!", "description":"Description!"})
        chapters.append({"links":[], "date":"2050-01-01", "title":"Not This", "description":"blah"})
        page = kemonocafe.get_page_info("paprika.kemono.cafe/comic/page-128", chapters)
        assert page["id"] == "paprika-page-128-shrodingers-pizza"
        assert page["title"] == "Page 128 – Shrodingers Pizza"
        assert page["url"] == "https://paprika.kemono.cafe/comic/page-128-shrodingers-pizza/"
        assert page["image_url"] == "https://paprika.kemono.cafe/wp-content/uploads/sites/3/2021/05/page128.png"
        assert page["date"] == "2021-05-11"
        assert page["comic"] == "Paprika"
        assert page["tagline"] == "Paprika | A Furry Webcomic by Nekonny"
        assert page["author"] == "Nekonny"
        assert page["chapter"] == "Chapter Name!"
        assert page["chapter_description"] == "Description!"
        assert page["post_content"].startswith("<p><emote character=\"ruby\"")
        assert page["post_content"].endswith("</emote></p>")
        assert "No one should hate their favorite pizza!" in page["post_content"]
        # Test loading page with improper date
        chapters = [{"links":[], "date":"2001-01-01", "title":"Not This", "description":"blah"}]
        chapters.append({"links":["theeye.kemono.cafe/comic/instant-abs"], "date":"2021-01-01", "title":"Last", "description":"Other"})
        chapters.append({"links":[], "date":"2050-01-01", "title":"Not This", "description":"blah"})
        page = kemonocafe.get_page_info("theeye.kemono.cafe/comic/instant-abs", chapters)
        assert page["id"] == "theeye-instant-abs"
        assert page["title"] == "Instant Abs"
        assert page["url"] == "https://theeye.kemono.cafe/comic/instant-abs/"
        assert page["image_url"] == "https://theeye.kemono.cafe/wp-content/uploads/sites/11/2020/04/final258.png"
        assert page["date"] == "2020-04-13"
        assert page["comic"] == "The Eye of Ramalach"
        assert page["tagline"] == "The Eye of Ramalach | A Furry Webcomic by Avencri"
        assert page["author"] == "avencrieggmaster"
        assert page["chapter"] == "Last"
        assert page["chapter_description"] == "Other"
        assert page["post_content"] is None

def test_download_page():
    """
    Tests the download_page method.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test if ID is already in the database
        config_file = abspath(join(temp_dir, "config.json"))
        archive_file = abspath(join(temp_dir, "kemonocafe.db"))
        config = {"kemonocafe":{"archive":archive_file, "metadata":True}}
        mm_file_tools.write_json_file(config_file, config)
        with KemonoCafe([config_file]) as kemonocafe:
            kemonocafe.initialize()
            json = {"title":"Page0001"}
            json["comic"] = "Addictive Science"
            json["url"] = "https://addictivescience.kemono.cafe/comic/page0001/"
            json["chapter"] = "Blah"
            kemonocafe.add_to_archive("kemonocafe-addictivescience-page0001")
            media_file = kemonocafe.download_page(json, temp_dir)
            assert media_file is None
        assert sorted(os.listdir(temp_dir)) == ["config.json", "kemonocafe.db"]
        # Test if file has not been written
        with KemonoCafe([config_file]) as kemonocafe:
            json = {"title":"Page0002"}
            json["id"] = "addictivescience-page0002"
            json["comic"] = "Addictive Science"
            json["chapter"] = "Ch1"
            json["url"] = "https://addictivescience.kemono.cafe/comic/page0002/"
            json["image_url"] = "https://addictivescience.kemono.cafe/wp-content/uploads/sites/12/2019/09/2013-01-02-page0002.jpg"
            media_file = kemonocafe.download_page(json, temp_dir)
            assert basename(media_file) == "addictivescience-page0002.jpg"
            assert exists(media_file)
        parent_folder = abspath(join(temp_dir, "KemonoCafe"))
        comic_folder = abspath(join(parent_folder, "Addictive Science"))
        chapter_folder = abspath(join(comic_folder, "Ch1"))
        assert exists(chapter_folder)
        json_file = abspath(join(chapter_folder, "addictivescience-page0002.json"))
        assert exists(json_file)
        meta = mm_file_tools.read_json_file(json_file)
        assert meta["title"] == "Page0002"
        assert meta["id"] == "addictivescience-page0002"
        assert meta["comic"] == "Addictive Science"
        assert meta["url"] == "https://addictivescience.kemono.cafe/comic/page0002/"
        assert meta["image_url"] == "https://addictivescience.kemono.cafe/wp-content/uploads/sites/12/2019/09/2013-01-02-page0002.jpg"
        assert os.stat(media_file).st_size == 452507
        # Test that ID has been written to the database
        with KemonoCafe([config_file]) as kemonocafe:
            kemonocafe.initialize()
            assert kemonocafe.archive_contains("kemonocafe-addictivescience-page0001")
            assert kemonocafe.archive_contains("kemonocafe-addictivescience-page0002")
            assert not kemonocafe.archive_contains("kemonocafe-addictivescience-page0003")
