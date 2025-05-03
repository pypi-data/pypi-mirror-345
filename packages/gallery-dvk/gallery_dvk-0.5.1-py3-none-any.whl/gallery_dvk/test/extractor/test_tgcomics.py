#!/usr/bin/env python3

import os
import tempfile
import gallery_dvk.extractor.tgcomics
import metadata_magic.file_tools as mm_file_tools
from gallery_dvk.extractor.tgcomics import TGComics
from os.path import abspath, basename, exists, join

def test_match_url():
    """
    Tests the match_url method.
    """
    with TGComics([]) as tgcomics:
        # Test getting artist and author pages
        match = tgcomics.match_url("https://tgcomics.com/tgc/artist/person/")
        assert match["section"] == "artist/person"
        assert match["type"] == "collection"
        match = tgcomics.match_url("www.tgcomics.com/tgc/artist/name")
        assert match["section"] == "artist/name"
        assert match["type"] == "collection"
        match = tgcomics.match_url("http://tgcomics.com/tgc/author/another")
        assert match["section"] == "author/another"
        assert match["type"] == "collection"
        match = tgcomics.match_url("tgcomics.com/tgc/author/blah/")
        assert match["section"] == "author/blah"
        assert match["type"] == "collection"
        # Test getting TGComics comic pages
        match = tgcomics.match_url("https://www.tgcomics.com/tgc/comics/another")
        assert match["section"] == "comics/another"
        assert match["type"] == "collection"
        match = tgcomics.match_url("www.tgcomics.com/tgc/comics/thing")
        assert match["section"] == "comics/thing"
        assert match["type"] == "collection"
        match = tgcomics.match_url("http://tgcomics.com/tgc/premium/deep/thing")
        assert match["section"] == "premium/deep/thing"
        assert match["type"] == "collection"
        match = tgcomics.match_url("tgcomics.com/tgc/comics/final/title/")
        assert match["section"] == "comics/final/title"
        assert match["type"] == "collection"
        # Test getting TGComics non-english pages
        match = tgcomics.match_url("https://www.tgcomics.com/tgc/es/comics/thing/")
        assert match["section"] == "es/comics/thing"
        assert match["type"] == "collection"
        match = tgcomics.match_url("www.tgcomics.com/tgc/ru/sequences/sequence-title")
        assert match["section"] == "ru/sequences/sequence-title"
        assert match["type"] == "collection"
        match = tgcomics.match_url("http://tgcomics.com/tgc/pt-br/portfolios/portfolio-por-person/")
        assert match["section"] == "pt-br/portfolios/portfolio-por-person"
        assert match["type"] == "collection"
        match = tgcomics.match_url("tgcomics.com/tgc/fr/artist/other-fr/")
        assert match["section"] == "fr/artist/other-fr"
        assert match["type"] == "collection"

def test_get_id():
    """
    Tests the get_id function.
    """
    with TGComics([]) as tgcomics:
        index = tgcomics.get_id("https://tgcontent.tgcomics.com/vignettes/image/THING.jpg")
        assert index == "tgcomics-vignettes/image/thing.jpg"
        index = tgcomics.get_id("www.tgcontent.tgcomics.com/videos/Person/video.mp4")
        assert index == "tgcomics-videos/person/video.mp4"
        index = tgcomics.get_id("tgcontent.tgcomics.com/comics/thing-pt-br/other.png")
        assert index == "tgcomics-comics/thing-pt-br/other.png"

def get_categories_test(tgcomics:TGComics):
    """
    Tests the get_categories method.
    Must be logged in to TGComics.com to work.
    
    :param tgcomics: TGComics extractor object, logged in to TGComics.com
    :type: TGComics, required
    """
    # Test getting all forms of category info
    tgcomics.initialize()
    tgcomics.cookies_to_header()
    bs = tgcomics.web_get("https://tgcomics.com/tgc/stories/reflections/")
    info = tgcomics.get_categories(bs)
    assert info["title"] == "Reflections"
    assert info["artists"] == ["Darkoshen"]
    assert info["authors"] == ["Bill Hart"]
    assert info["age_rating"] == "TGC-R"
    assert info["genres"] == ["Magic"]
    assert info["sexual_preferences"] == ["Post-Hetero", "Pre-Hetero"]
    assert info["transformations"] == ["Full XX Change", "Instant Transformation",
            "Magical Transformation", "Male-to-Female Transformation"]
    assert info["transformation_details"] == ["Bad Boy to Good Girl", "Identity Death",
            "Mental Reconditioning", "Process Shown", "Reality Alteration", "Witchcraft"]
    assert info["status"] == "Complete"
    assert info["date"] == "2016-03-07"
    # Test if some forms are missing
    bs = tgcomics.web_get("https://tgcomics.com/tgc/comics/raans-doll/")
    info = tgcomics.get_categories(bs)
    assert info["title"] == "Raan’s Doll"
    assert info["artists"] == ["Kannel"]
    assert info["authors"] is None
    assert info["age_rating"] == "TGC-R"
    assert info["genres"] == ["Romance", "Slice of Life"]
    assert info["sexual_preferences"] == ["Post-Unsure", "Pre-Hetero"]
    assert info["transformations"] == ["Crossdressing and TV", "Partial Transformation", "Slow Transformation"]
    assert info["transformation_details"] == ["Female Domination"]
    assert info["status"] == "Ongoing - Updated sporadically"
    assert info["date"] == "2021-08-21"
    # Test with multiple artists
    bs = tgcomics.web_get("https://tgcomics.com/tgc/comics/angelas-trick-n-treat-2020/")
    info = tgcomics.get_categories(bs)
    assert info["title"] == "Angela’s Tyler’s Trick ’n Treat (2020 Edition)"
    assert info["artists"] == ["TGTrinity", "NotZackforWork"]
    assert info["authors"] is None
    assert info["age_rating"] is None
    assert info["genres"] is None
    assert info["sexual_preferences"] is None
    assert info["transformations"] is None
    assert info["transformation_details"] is None
    assert info["status"] is None
    assert info["date"] == "2020-10-31"
    # Test getting category info from a page that doesn't have it
    bs = tgcomics.web_get("https://tgcomics.com/tgc/comics/")
    info = tgcomics.get_categories(bs)
    assert info["title"] == "Comics"
    assert info["artists"] is None
    assert info["authors"] is None
    assert info["age_rating"] is None
    assert info["genres"] is None
    assert info["sexual_preferences"] is None
    assert info["transformations"] is None
    assert info["transformation_details"] is None
    assert info["status"] is None
    assert info["date"] is None
    bs = tgcomics.web_get("https://tgcomics.com/tgc/")
    info = tgcomics.get_categories(bs)
    assert info["title"] is None
    assert info["artists"] is None
    assert info["authors"] is None
    assert info["age_rating"] is None
    assert info["genres"] is None
    assert info["sexual_preferences"] is None
    assert info["transformations"] is None
    assert info["transformation_details"] is None
    assert info["status"] is None
    assert info["date"] is None

def get_pages_from_collection_test(tgcomics:TGComics):
    """
    Tests the get_pages_from_collection method.
    Must be logged in to TGComics.com to work.
    
    :param tgcomics: TGComics extractor object, logged in to TGComics.com
    :type: TGComics, required
    """
    # Test getting pages from artists gallery
    pages = tgcomics.get_pages_from_collection("artist/kittyhawk")
    assert len(pages) == 3
    assert pages[0]["page_url"] == "vignettes/out-of-town"
    assert pages[0]["collection_description"] == "Two young men find a new way to while away the time while housesitting."
    assert pages[0]["transformations"] is None
    assert pages[0]["date"] is None
    assert pages[1]["page_url"] == "vignettes/model"
    assert pages[1]["collection_description"] == "Until now, I was a man..."
    assert pages[1]["transformations"] is None
    assert pages[2]["page_url"] == "vignettes/kittyhawk-vignettes"
    description = "Short, witty and wonderful transformation comics from the creator of "
    description = f"{description}<a href=\"http://Sparkling Generation Valkyrie Yuuki\" " 
    description = f"{description}target=\"_blank\">Sparkling Generation Valkyrie Yuuki</a> and other works."
    assert pages[2]["collection_description"] == description
    # Test getting pages in another format
    pages = tgcomics.get_pages_from_collection("vignettes/out-of-town", {"collection_description":None})
    assert len(pages) == 2
    assert pages[0]["page_url"] == "vignettes/out-of-town/out-of-town-part-1"
    assert pages[0]["collection_description"] is None
    assert pages[0]["title"] == "Out of Town"
    assert pages[0]["artists"] == ["Kittyhawk"]
    assert pages[0]["authors"] == ["Ankan"]
    assert pages[0]["age_rating"] == "TGC-X"
    assert pages[0]["genres"] == ["Humor"]
    assert pages[0]["transformations"] == ["Full XX Change",
            "Future Science Transformation", "Instant Transformation"]
    assert pages[0]["transformation_details"] == ["Process Shown", "Willing or Voluntary"]
    assert pages[0]["sexual_preferences"] == ["Post-Hetero", "Pre-Hetero"]
    assert pages[0]["status"] == "Complete"
    assert pages[0]["date"] == "2014-10-14"
    assert pages[0]["cover_image"] is None
    assert pages[0]["cover_page"] is None
    assert pages[1]["page_url"] == "vignettes/out-of-town/out-of-town-part-2"
    # Test getting pages from artists gallery with multiple pages
    pages = tgcomics.get_pages_from_collection("infinity-sign")
    length = len(pages)
    assert length > 74
    assert pages[length-75]["page_url"] == "vignettes/coconut-milk"
    assert pages[length-75]["collection_description"] == "When it's a lovely day at the beach... there's nothing quite like a cold drink!"
    assert pages[length-75]["transformations"] is None
    assert pages[length-75]["date"] is None
    assert pages[length-1]["page_url"] == "comics/complex-eve"
    assert pages[length-1]["collection_description"].startswith("Eric is out of work and desperate,")
    # Test getting pages from comic gallery
    pages = tgcomics.get_pages_from_collection("comics/raans-doll/", {"collection_description":"Test Description"})
    assert len(pages) == 5
    assert pages[0]["page_url"] == "comics/raans-doll/raans-doll-chapter-1"
    assert pages[0]["collection_description"] == "Test Description"
    assert pages[0]["title"] == "Raan’s Doll"
    assert pages[0]["artists"] == ["Kannel"]
    assert pages[0]["authors"] is None
    assert pages[0]["age_rating"] == "TGC-R"
    assert pages[0]["genres"] == ["Romance", "Slice of Life"]
    assert pages[0]["transformations"] == ["Crossdressing and TV", "Partial Transformation", "Slow Transformation"]
    assert pages[0]["transformation_details"] == ["Female Domination"]
    assert pages[0]["sexual_preferences"] == ["Post-Unsure", "Pre-Hetero"]
    assert pages[0]["status"] == "Ongoing - Updated sporadically"
    assert pages[0]["date"] == "2021-08-21"
    assert pages[0]["cover_image"] is None
    assert pages[0]["cover_page"] is None
    assert pages[1]["page_url"] == "comics/raans-doll/raans-doll-chapter-2"
    assert pages[2]["page_url"] == "comics/raans-doll/raans-doll-chapter-3"
    assert pages[3]["page_url"] == "comics/raans-doll/raans-doll-chapter-4"
    assert pages[4]["page_url"] == "comics/raans-doll/raans-doll-singles-and-shorts"
    # Test getting pages from story gallery
    pages = tgcomics.get_pages_from_collection("second-sight", {"transformation_details":["Test"], "collection_description":None})
    assert len(pages) == 38
    assert pages[0]["page_url"] == "stories/second-sight/second-sight-chapter-1"
    assert pages[0]["collection_description"] is None
    assert pages[0]["title"] == "Second Sight"
    assert pages[0]["artists"] == ["Darkoshen"]
    assert pages[0]["authors"] == ["Lilac Wren"]
    assert pages[0]["age_rating"] == "TGC-R"
    assert pages[0]["genres"] == ["Supernatural"]
    assert pages[0]["transformations"] == ["Full XX Change", "Instant Transformation", "Male-to-Female Transformation"]
    assert pages[0]["transformation_details"] == ["Test"]
    assert pages[0]["sexual_preferences"] == ["Post-Hetero", "Pre-Hetero"]
    assert pages[0]["status"] == "Complete"
    assert pages[0]["date"] == "2016-09-11"
    assert pages[0]["cover_image"] == "https://tgcontent.tgcomics.com/stories/second-sight/second-sight-000.jpg"
    assert pages[0]["cover_page"] == "stories/second-sight"
    assert pages[1]["page_url"] == "stories/second-sight/second-sight-chapter-2"
    assert pages[2]["page_url"] == "stories/second-sight/second-sight-chapter-3"
    assert pages[35]["page_url"] == "stories/second-sight/second-sight-chapter-36"
    assert pages[36]["page_url"] == "stories/second-sight/second-sight-chapter-37"
    assert pages[37]["page_url"] == "stories/second-sight/second-sight-epilogue"
    # Test getting pages with cover image
    pages = tgcomics.get_pages_from_collection("comics/the-heel")
    assert len(pages) == 5
    assert pages[0]["page_url"] == "comics/the-heel/the-heel-chapter-1"
    assert pages[0]["collection_description"] is None
    assert pages[0]["title"] == "The Heel"
    assert pages[0]["artists"] == ["Kannel"]
    assert pages[0]["authors"] is None
    assert pages[0]["age_rating"] == "TGC-M"
    assert pages[0]["genres"] == ["Adventure", "Humor"]
    assert pages[0]["transformations"] == ["Chemical Transformation", "Full XX Change",
            "Future Science Transformation", "Male-to-Female Transformation"]
    assert pages[0]["transformation_details"] == ["For a Job", "Medical Experiment"]
    assert pages[0]["sexual_preferences"] == ["Post-Hetero", "Pre-Hetero"]
    assert pages[0]["status"] == "Complete"
    assert pages[0]["date"] == "2015-10-02"
    assert pages[0]["cover_image"] == "https://tgcontent.tgcomics.com/comics/the-heel/the-heel-cover.jpg"
    assert pages[0]["cover_page"] == "comics/the-heel"
    assert pages[1]["page_url"] == "comics/the-heel/the-heel-chapter-2"
    assert pages[2]["page_url"] == "comics/the-heel/the-heel-chapter-3"
    assert pages[3]["page_url"] == "comics/the-heel/the-heel-chapter-4"
    assert pages[4]["page_url"] == "comics/the-heel/the-heel-chapter-5xxx"
    # Test if the page is an image page
    pages = tgcomics.get_pages_from_collection("out-of-town-part-2", {"collection_description":"Thing"})
    assert len(pages) == 9
    assert pages[0]["collection_description"] == "Thing"
    assert pages[0]["artists"] == ["Kittyhawk"]
    assert pages[0]["authors"] == ["Ankan"]
    assert pages[0]["date"] == "2014-10-04"
    assert pages[0]["age_rating"] is None
    assert pages[0]["genres"] is None
    assert pages[0]["transformations"] is None
    assert pages[0]["transformation_details"] is None
    assert pages[0]["sexual_preferences"] is None
    assert pages[0]["status"] is None
    assert pages[0]["page_url"] == "https://tgcomics.com/tgc/vignettes/out-of-town/out-of-town-part-2/"
    assert pages[0]["title"] == "Out of Town – Part Two [Page 1]"
    assert pages[0]["url"] == "https://tgcontent.tgcomics.com/vignettes/out-of-town/out-of-town2/out-of-town2-01.jpg"
    assert pages[0]["description"] == "Thing"
    assert pages[6]["title"] == "Out of Town – Part Two [Page 7]"
    assert pages[6]["url"] == "https://tgcontent.tgcomics.com/vignettes/out-of-town/out-of-town2/out-of-town2-07.jpg"
    assert pages[6]["description"] == "<span class=\"cont\">To be continued...?</span>"
    assert pages[7]["title"] == "Out of Town – Part Two [PDF]"
    assert pages[7]["url"] == "https://tgcontent.tgcomics.com/vignettes/out-of-town/out-of-town2/out-of-town2.pdf"
    assert pages[7]["description"] == "Thing"
    assert pages[8]["title"] == "Out of Town – Part Two [ZIP]"
    assert pages[8]["url"] == "https://tgcontent.tgcomics.com/vignettes/out-of-town/out-of-town2/out-of-town2.zip"
    assert pages[8]["description"] == "Thing"
    # Test if the page is a video page
    pages = tgcomics.get_pages_from_collection("videos/peephole", {"collection_description":"Another"})
    assert len(pages) == 1
    assert pages[0]["collection_description"] == "Another"
    assert pages[0]["artists"] == ["TGedNathan"]
    assert pages[0]["authors"] is None
    assert pages[0]["date"] == "2022-10-12"
    assert pages[0]["age_rating"] == "TGC-R"
    assert pages[0]["genres"] ==  ["Magic"]
    assert pages[0]["transformations"] == ["Magical Transformation", "Male-to-Female Transformation"]
    assert pages[0]["transformation_details"] == ["Transformation as Punishment"]
    assert pages[0]["sexual_preferences"] == ["Post-Unsure", "Pre-Hetero"]
    assert pages[0]["status"] == "Complete"
    assert pages[0]["page_url"] == "https://tgcomics.com/tgc/videos/peephole/"
    assert pages[0]["title"] == "Peephole"
    assert pages[0]["url"] == "https://tgcontent.tgcomics.com/videos/peephole/peephole.mp4"
    assert pages[0]["description"] == "Another"
    # Test with non-purchased premium comic
    bs = tgcomics.web_get("https://tgcomics.com/tgc/premium-preview/perfect-heist-preview/")
    assert tgcomics.get_image_pages(bs) == []

def test_get_cover_page():
    """
    Tests the get_cover_page function.
    """
    # Test converting cover information to image information
    input_page = dict()
    input_page["page_url"] = "comics/the-heel/the-heel-chapter-1"
    input_page["collection_description"] = "Something"
    input_page["title"] = "The Heel"
    input_page["artists"] = ["Kannel"]
    input_page["authors"] = None
    input_page["age_rating"] = "TGC-M"
    input_page["genres"] = ["Adventure", "Humor"]
    input_page["status"] = "Complete"
    input_page["date"] = "2015-10-02"
    input_page["cover_image"] = "https://tgcontent.tgcomics.com/comics/the-heel/the-heel-cover.jpg"
    input_page["cover_page"] = "comics/the-heel"
    output_page = gallery_dvk.extractor.tgcomics.get_cover_page(input_page)
    assert output_page["collection_description"] == "Something"
    assert output_page["description"] == "Something"
    assert output_page["title"] == "The Heel"
    assert output_page["artists"] == ["Kannel"]
    assert output_page["authors"] == None
    assert output_page["age_rating"] == "TGC-M"
    assert output_page["genres"] == ["Adventure", "Humor"]
    assert output_page["status"] == "Complete"
    assert output_page["date"] == "2015-10-02"
    assert output_page["url"] == "https://tgcontent.tgcomics.com/comics/the-heel/the-heel-cover.jpg"
    assert output_page["page_url"] == "https://tgcomics.com/tgc/comics/the-heel/"
    assert output_page["cover_image"] is None
    assert output_page["cover_page"] is None
    # Test if there is no cover information
    assert gallery_dvk.extractor.tgcomics.get_cover_page({}) is None
    assert gallery_dvk.extractor.tgcomics.get_cover_page({"blah":"blah"}) is None
    assert gallery_dvk.extractor.tgcomics.get_cover_page({"cover_image":None}) is None
    assert gallery_dvk.extractor.tgcomics.get_cover_page({"cover_image":"YAY", "cover_page":None}) is None

def get_image_pages_test(tgcomics:TGComics):
    """
    Tests the get_image_pages method.
    Must be logged in to TGComics.com to work.
    
    :param tgcomics: TGComics extractor object, logged in to TGComics.com
    :type: TGComics, required
    """
    # Test getting page with no thumbnails or titles
    tgcomics.initialize()
    tgcomics.cookies_to_header()
    bs = tgcomics.web_get("https://tgcomics.com/tgc/out-of-town-part-1")
    metadata = {"collection_description":"Thing", "transformations":["testing"], "cover_image":None, "cover_page":None}
    pages = tgcomics.get_image_pages(bs, metadata)
    assert len(pages) == 6
    try:
        assert pages[0]["cover_image"] == 1
    except KeyError:pass
    try:
        assert pages[0]["cover_page"] == 1
    except KeyError:pass
    assert pages[0]["collection_description"] == "Thing"
    assert pages[0]["artists"] == ["Kittyhawk"]
    assert pages[0]["authors"] == ["Ankan"]
    assert pages[0]["description"] == "Thing"
    assert pages[0]["transformations"] == ["testing"]
    assert pages[0]["genres"] is None
    assert pages[0]["date"] == "2014-05-03"
    assert pages[0]["page_url"] == "https://tgcomics.com/tgc/vignettes/out-of-town/out-of-town-part-1/"
    assert pages[0]["title"] == "Out of Town – Part One [Page 1]"
    assert pages[0]["url"] == "https://tgcontent.tgcomics.com/vignettes/out-of-town/out-of-town1/out-of-town1-01.jpg"
    assert pages[0]["id"] == "out-of-town1-01.jpg"
    assert pages[1]["title"] == "Out of Town – Part One [Page 2]"
    assert pages[1]["url"] == "https://tgcontent.tgcomics.com/vignettes/out-of-town/out-of-town1/out-of-town1-02.jpg"
    assert pages[1]["id"] == "out-of-town1-02.jpg"
    assert pages[2]["title"] == "Out of Town – Part One [Page 3]"
    assert pages[2]["url"] == "https://tgcontent.tgcomics.com/vignettes/out-of-town/out-of-town1/out-of-town1-03.jpg"
    assert pages[2]["id"] == "out-of-town1-03.jpg"
    assert pages[3]["title"] == "Out of Town – Part One [Page 4]"
    assert pages[3]["url"] == "https://tgcontent.tgcomics.com/vignettes/out-of-town/out-of-town1/out-of-town1-04.jpg"
    assert pages[3]["id"] == "out-of-town1-04.jpg"
    assert pages[4]["title"] == "Out of Town – Part One [Page 5]"
    assert pages[4]["url"] == "https://tgcontent.tgcomics.com/vignettes/out-of-town/out-of-town1/out-of-town1-05.jpg"
    assert pages[4]["id"] == "out-of-town1-05.jpg"
    assert pages[5]["title"] == "Out of Town – Part One [Page 6]"
    assert pages[5]["url"] == "https://tgcontent.tgcomics.com/vignettes/out-of-town/out-of-town1/out-of-town1-06.jpg"
    assert pages[5]["id"] == "out-of-town1-06.jpg"    
    # Test getting a large amount of pages
    tgcomics.cookies_to_header()
    bs = tgcomics.web_get("https://tgcomics.com/tgc/comics/open-trade/")
    metadata = {"transformations":["overwrite"], "cover_image":None, "cover_image":None}
    pages = tgcomics.get_image_pages(bs, metadata)
    length = len(pages)
    assert length > 175
    assert pages[0]["collection_description"] is None
    assert pages[0]["artists"] == ["Roseleaf"]
    assert pages[0]["authors"] is None
    assert pages[0]["description"] is None
    assert pages[0]["date"] is not None
    assert pages[0]["age_rating"] == "TGC-R"
    assert pages[0]["genres"] == ["Humor", "Science Fiction"]
    assert pages[0]["transformations"] == ["Full XX Change", "Magical Transformation",
            "Male-to-Female Transformation", "Slow Transformation"]
    assert pages[0]["transformation_details"] == ["Deal/Bet/Dare", "Mental Reconditioning",
            "Process Shown", "Willing or Voluntary"]
    assert pages[0]["sexual_preferences"] == ["Post-Bisexual", "Pre-Hetero"]
    assert pages[0]["status"] == "Ongoing - Updated regularly"
    assert pages[0]["page_url"] == "https://tgcomics.com/tgc/comics/open-trade/"
    assert pages[0]["title"] == "Open Trade [Page 1]"
    assert pages[0]["url"] == "https://tgcontent.tgcomics.com/comics/open-trade/open-trade-001.jpg"
    assert pages[0]["id"] == "open-trade-001.jpg"
    assert pages[175]["title"] == "Open Trade [Page 176]"
    assert pages[175]["url"] == "https://tgcontent.tgcomics.com/comics/open-trade/open-trade-176.jpg"
    assert pages[175]["id"] == "open-trade-176.jpg"
    # Test getting pages with added titles and descriptions
    tgcomics.cookies_to_header()
    bs = tgcomics.web_get("https://tgcomics.com/tgc/notzackforwork-portfolio")
    metadata = {"collection_description":"Thing", "cover_image":None, "cover_image":None}
    pages = tgcomics.get_image_pages(bs, metadata)
    assert len(pages) == 26
    assert pages[0]["collection_description"] == "Thing"
    assert pages[0]["artists"] == ["NotZackforWork"]
    assert pages[0]["authors"] is None
    assert pages[0]["date"] == "2020-09-21"
    assert pages[0]["age_rating"] is None
    assert pages[0]["genres"] is None
    assert pages[0]["transformations"] is None
    assert pages[0]["transformation_details"] is None
    assert pages[0]["sexual_preferences"] is None
    assert pages[0]["status"] is None
    assert pages[0]["page_url"] == "https://tgcomics.com/tgc/portfolios/notzackforwork-portfolio/"
    assert pages[0]["title"] == "NotZackforWork’s Portfolio [Helen (for Dr. Beaubourg)]"
    assert pages[0]["url"] == "https://tgcontent.tgcomics.com/portfolios/notzackforwork/helen-dr-beaubourg.jpg"
    assert pages[0]["id"] == "helen-dr-beaubourg.jpg"
    description = "This was commissioned by <a href=\"https://www.deviantart.com/drbeaubourg\" "
    description = f"{description}rel=\"noopener\" target=\"_blank\">Dr.Beaubourg</a> and "
    description = f"{description}features Helen Campbell, the MILF alternate identity<br/>of "
    description = f"{description}Marty Campbell (from Dr.Beaubourg's MILF Machine stories)."
    assert pages[0]["description"] == description
    assert pages[25]["title"] == "NotZackforWork’s Portfolio [Playboy Style Cartoon 2]"
    assert pages[25]["url"] == "https://tgcontent.tgcomics.com/portfolios/notzackforwork/playboy-style-02.jpg"
    assert pages[25]["id"] == "playboy-style-02.jpg"
    description = "Sexy cartoons done in that classic magazine style!"
    assert pages[25]["description"] == description
    # Test with a non-image pages
    tgcomics.cookies_to_header()
    bs = tgcomics.web_get("https://tgcomics.com/tgc/")
    assert tgcomics.get_image_pages(bs) == []
    bs = tgcomics.web_get("https://tgcomics.com/tgc/author/")
    assert tgcomics.get_image_pages(bs) == []
    bs = tgcomics.web_get("https://tgcomics.com/tgc/stories/reflections/")
    assert tgcomics.get_image_pages(bs) == []
    bs = tgcomics.web_get("https://tgcomics.com/tgc/videos/swap-io/")
    assert tgcomics.get_image_pages(bs) == []
    # Test with non-purchased premium comic
    bs = tgcomics.web_get("https://tgcomics.com/tgc/premium-preview/perfect-heist-preview/")
    assert tgcomics.get_image_pages(bs) == []

def get_video_page_test(tgcomics:TGComics):
    """
    Tests the get_video_page method.
    Must be logged in to TGComics.com to work.
    
    :param tgcomics: TGComics extractor object, logged in to TGComics.com
    :type: TGComics, required
    """
    tgcomics.initialize()
    tgcomics.cookies_to_header()
    # Test getting video with no description
    bs = tgcomics.web_get("https://tgcomics.com/tgc/videos/cchimeras-powerful-knead/")
    metadata = {"collection_description":"Desc", "transformations":["testing"], "cover_page":None}
    page = tgcomics.get_video_page(bs, metadata)
    try:
        assert page["cover_image"] == 1
    except KeyError:pass
    try:
        assert page["cover_page"] == 1
    except KeyError:pass
    assert page["collection_description"] == "Desc"
    assert page["description"] == "Desc"
    assert page["artists"] == ["Cchimeras"]
    assert page["authors"] is None
    assert page["age_rating"] is None
    assert page["transformations"] == ["testing"]
    assert page["genres"] is None
    assert page["date"] == "2023-02-20"
    assert page["status"] is None
    assert page["page_url"] == "https://tgcomics.com/tgc/videos/cchimeras-transformations/cchimeras-powerful-knead/"
    assert page["title"] == "A Powerful Knead"
    assert page["url"] == "https://tgcontent.tgcomics.com/videos/cchimeras/cchimeras-transformations-powerful-knead.mp4"
    assert page["id"] == "cchimeras-transformations-powerful-knead.mp4"
    # Test getting video with description
    bs = tgcomics.web_get("https://tgcomics.com/tgc/swap-io/")
    metadata = {"transformations":["testing"], "cover_image":None, "cover_page":None}
    page = tgcomics.get_video_page(bs, metadata)
    try:
        assert page["cover_image"] == 1
    except KeyError:pass
    try:
        assert page["cover_page"] == 1
    except KeyError:pass
    assert page["collection_description"] is None
    assert page["description"] is None
    assert page["artists"] == ["TGedNathan"]
    assert page["authors"] == None
    assert page["age_rating"] == "TGC-C"
    assert page["transformations"] == ["Female-to-Male Transformation", "Future Science Transformation",
            "Male-to-Female Transformation", "Multiple Transformations"]
    assert page["genres"] == ["Science Fiction"]
    assert page["date"] == "2022-12-31"
    assert page["status"] == "Complete"
    assert page["page_url"] == "https://tgcomics.com/tgc/videos/swap-io/"
    assert page["title"] == "Swap IO"
    assert page["url"] == "https://tgcontent.tgcomics.com/videos/swap-io/swap-io.mp4"
    assert page["id"] == "swap-io.mp4"
    # Test getting a non-video page
    bs = tgcomics.web_get("https://tgcomics.com/tgc/vignettes/st-patricks-day-miracle/")
    assert tgcomics.get_video_page(bs, {}) is None
    bs = tgcomics.web_get("https://tgcomics.com/tgc/")
    assert tgcomics.get_video_page(bs, {}) is None

def get_archive_pages_test(tgcomics:TGComics):
    """
    Tests the get_archive_pages method.
    Must be logged in to TGComics.com to work.
    
    :param tgcomics: TGComics extractor object, logged in to TGComics.com
    :type: TGComics, required
    """
    # Test getting page with both a PDF and a ZIP archive
    tgcomics.initialize()
    tgcomics.cookies_to_header()
    bs = tgcomics.web_get("https://tgcomics.com/tgc/out-of-town-part-1")
    metadata = {"collection_description":"Thing", "transformations":["Different"], "cover_image":None, "cover_page":None}
    pages = tgcomics.get_archive_pages(bs, metadata)
    assert len(pages) == 2
    try:
        assert pages[0]["cover_image"] == 1
    except KeyError:pass
    try:
        assert pages[0]["cover_page"] == 1
    except KeyError:pass
    assert pages[0]["collection_description"] == "Thing"
    assert pages[0]["artists"] == ["Kittyhawk"]
    assert pages[0]["authors"] == ["Ankan"]
    assert pages[0]["description"] == "Thing"
    assert pages[0]["transformations"] == ["Different"]
    assert pages[0]["genres"] is None
    assert pages[0]["date"] == "2014-05-03"
    assert pages[0]["page_url"] == "https://tgcomics.com/tgc/vignettes/out-of-town/out-of-town-part-1/"
    assert pages[0]["title"] == "Out of Town – Part One [PDF]"
    assert pages[0]["url"] == "https://tgcontent.tgcomics.com/vignettes/out-of-town/out-of-town1/out-of-town1.pdf"
    assert pages[0]["id"] == "out-of-town1.pdf"
    assert pages[1]["collection_description"] == "Thing"
    assert pages[1]["artists"] == ["Kittyhawk"]
    assert pages[1]["authors"] == ["Ankan"]
    assert pages[1]["description"] == "Thing"
    assert pages[1]["transformations"] == ["Different"]
    assert pages[1]["genres"] is None
    assert pages[1]["date"] == "2014-05-03"
    assert pages[1]["page_url"] == "https://tgcomics.com/tgc/vignettes/out-of-town/out-of-town-part-1/"
    assert pages[1]["title"] == "Out of Town – Part One [ZIP]"
    assert pages[1]["url"] == "https://tgcontent.tgcomics.com/vignettes/out-of-town/out-of-town1/out-of-town1.zip"
    assert pages[1]["id"] == "out-of-town1.zip"
    # Test getting page with only PDF
    bs = tgcomics.web_get("https://tgcomics.com/tgc/stories/reflections")
    metadata = {"collection_description":"NEW"}
    pages = tgcomics.get_archive_pages(bs, metadata)
    assert len(pages) == 1
    assert pages[0]["collection_description"] == "NEW"
    assert pages[0]["artists"] == ["Darkoshen"]
    assert pages[0]["authors"] == ["Bill Hart"]
    assert pages[0]["age_rating"] == "TGC-R"
    assert pages[0]["description"] == "NEW"
    assert pages[0]["transformations"] == ["Full XX Change", "Instant Transformation",
            "Magical Transformation", "Male-to-Female Transformation"]
    assert pages[0]["transformation_details"] == ["Bad Boy to Good Girl", "Identity Death",
            "Mental Reconditioning", "Process Shown", "Reality Alteration", "Witchcraft"]
    assert pages[0]["sexual_preferences"] == ["Post-Hetero", "Pre-Hetero"]
    assert pages[0]["genres"] == ["Magic"]
    assert pages[0]["date"] == "2016-03-07"
    assert pages[0]["status"] == "Complete"
    assert pages[0]["page_url"] == "https://tgcomics.com/tgc/stories/reflections/"
    assert pages[0]["title"] == "Reflections [PDF]"
    assert pages[0]["url"] == "https://tgcontent.tgcomics.com/stories/reflections/reflections.pdf"
    assert pages[0]["id"] == "reflections.pdf"
    # Test getting page with no archives
    bs = tgcomics.web_get("https://tgcomics.com/tgc/videos/cchimeras-transformations/cchimeras-reassembly-required/")
    assert tgcomics.get_archive_pages(bs, metadata) == []
    bs = tgcomics.web_get("https://tgcomics.com/tgc/")
    assert tgcomics.get_archive_pages(bs, metadata) == []

def download_page_test(tgcomics:TGComics, temp_dir:str):
    """
    Tests the download_pages method.
    Must be logged in to TGComics.com to work.
    
    :param tgcomics: TGComics extractor object, logged in to TGComics.com
    :type: TGComics, required
    :param temp_dir: Path to the test directory containing archive info.
    :type temp_dir: str, required
    """
    # Test if ID is already in the database
    json = {"title":"Out of Town [Page 1]"}
    json["url"] = "https://tgcontent.tgcomics.com/vignettes/out-of-town/out-of-town1/out-of-town1-01.jpg"
    json["page_url"] = "https://tgcomics.com/tgc/vignettes/out-of-town/out-of-town-part-1/"
    json["artist"] = "Kittyhawk"
    tgcomics.add_to_archive("tgcomics-vignettes/out-of-town/out-of-town1/out-of-town1-01.jpg")
    media_file = tgcomics.download_page(json, temp_dir)
    assert media_file is None
    files = sorted(os.listdir(temp_dir)) == ["config.json", "tgcomics.db"]
    # Test if file has not been written
    json = {"title":"Out of Town [Page 2]"}
    json["artists"] = ["Kittyhawk"]
    json["authors"] = ["Ankan"]
    json["url"] = "https://tgcontent.tgcomics.com/vignettes/out-of-town/out-of-town1/out-of-town1-02.jpg"
    json["page_url"] = "https://tgcomics.com/tgc/vignettes/out-of-town/out-of-town-part-1/"
    media_file = tgcomics.download_page(json, temp_dir)
    assert basename(media_file) == "Out of Town [Page 2].jpg"
    assert exists(media_file)
    media_dir = abspath(join(temp_dir, "tgcomics"))
    media_dir = abspath(join(media_dir, "Kittyhawk"))
    media_dir = abspath(join(media_dir, "vignettes"))
    media_dir = abspath(join(media_dir, "out-of-town"))
    media_dir = abspath(join(media_dir, "out-of-town-part-1"))
    assert exists(media_dir)
    json_file = abspath(join(media_dir, "Out of Town [Page 2].json"))
    assert exists(json_file)
    meta = mm_file_tools.read_json_file(json_file)
    assert meta["title"] == "Out of Town [Page 2]"
    assert meta["artists"] == ["Kittyhawk"]
    assert meta["authors"] == ["Ankan"]
    assert meta["url"] == "https://tgcontent.tgcomics.com/vignettes/out-of-town/out-of-town1/out-of-town1-02.jpg"
    assert meta["page_url"] == "https://tgcomics.com/tgc/vignettes/out-of-town/out-of-town-part-1/"
    assert os.stat(media_file).st_size == 276099
    # Test that ID has been written to the database
    assert tgcomics.archive_contains("tgcomics-vignettes/out-of-town/out-of-town1/out-of-town1-01.jpg")
    assert tgcomics.archive_contains("tgcomics-vignettes/out-of-town/out-of-town1/out-of-town1-02.jpg")
    assert not tgcomics.archive_contains("tgcomics-image/thing.png")

def test_with_login():
    """
    Tests getting info from TGComics pages that are unavailable when not logged in.
    Requires a user config file with TGComics username and password to pass.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        archive_file = abspath(join(temp_dir, "tgcomics.db"))
        with TGComics() as tgcomics:
            # Nullify archive_file so user archive isn't overwritten
            try:
                tgcomics.archive_connection.close()
            except AttributeError: pass
            tgcomics.filename_format = "{title}"
            tgcomics.archive_file = archive_file
            tgcomics.open_archive()
            tgcomics.write_metadata = True
            # Test logging in
            if tgcomics.username is None or tgcomics.password is None:
                raise Exception("TGComics Username and Password must be provided in a user config file to perform this test.")
            assert tgcomics.login(tgcomics.username, tgcomics.password)
            assert tgcomics.attempted_login
            # Test getting categories from a page
            get_categories_test(tgcomics)
            # Test getting the image pages
            get_image_pages_test(tgcomics)
            # Test getting the video page
            get_video_page_test(tgcomics)
            # Test getting the archive pages
            get_archive_pages_test(tgcomics)
            # Test pages from collection
            get_pages_from_collection_test(tgcomics)
            # Test downloading pages
            download_page_test(tgcomics, temp_dir)
