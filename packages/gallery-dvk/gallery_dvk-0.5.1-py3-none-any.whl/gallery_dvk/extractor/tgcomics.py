#!/usr/bin/env python3

import re
import bs4
import copy
import gallery_dvk
import gallery_dvk.extractor.extractor as gd_extractor
import metadata_magic.file_tools as mm_file_tools
from typing import List

def get_cover_page(collection_page:dict) -> dict:
    """
    Takes the page info from a TGComics collection page and converts it to image page info based on the cover image.
    Cover image is in the format of the dictionaries returned by TGComics.get_image_page
    If there is no cover image information in the given page, None is returned.
    
    :param collection_page: Collection page info as returned by TGComics.get_pages_from_collection
    :type collection_page: dict, required
    :return: Image page as returned by TGComics.get_image_page
    :rtype: dict
    """
    # Get the cover image
    try:
        cover_image = collection_page["cover_image"]
        cover_page = collection_page["cover_page"]
        assert cover_image is not None
        assert cover_page is not None
    except (KeyError, AssertionError): return None
    # Create the cover page dictionary
    image_page = copy.deepcopy(collection_page)
    image_page["url"] = cover_image
    image_page["page_url"] = f"https://tgcomics.com/tgc/{cover_page}/"
    image_page["cover_image"] = None
    image_page["cover_page"] = None
    image_page["description"] = image_page["collection_description"]
    # Return the image page
    return image_page

class TGComics(gd_extractor.Extractor):
    def __init__(self, config_paths:List[str]=gallery_dvk.config.get_default_config_paths()):
        """
        Creates the TGComics object and loads configuration files.
        
        :param config_paths: Paths to attempt to read as a configuration file, defaults to default config paths
        :type config_paths: list[str]
        """
        super().__init__(category="tgcomics", config_paths=config_paths)
        # Set the URL matchers
        self.url_matchers = []
        self.section = r"(?<=tgcomics\.com\/tgc\/).+[^\/](?=\/?$)"
        match = r"(?:https?:\/\/)?(?:www\.)?tgcomics\.com\/tgc\/.+$"
        self.url_matchers.append({"match":match, "section":self.section, "type":"collection"})        
        # Set the default filename format, if necessary
        if self.filename_format == "{title}":
            self.filename_format = "{id}_{title}"
    
    def get_id(self, url:str) -> str:
        """
        Gets the id for a TGComics media page.

        :param url: TGComics media page URL
        :type url: str, required
        :return: ID for the media URL
        :rtype: str
        """
        identifier = re.findall(r"(?<=tgcontent\.tgcomics\.com\/).+$", url.lower())[0]
        return f"tgcomics-{identifier}"
    
    def download_collection(self, section:str, directory:str) -> bool:
        """
        Attempt to download a TGComics collection.
        Can either be a full gallery or just a single comic.
        
        :param section: Section of URL used to get collection
        :type section: str, required
        :param directory: Directory to save files into
        :type directory: str, required
        :return: Whether download was successful
        :rtype: bool
        """
        # Get the initial set of pages
        print(f"Scanning \".../{section}\"")
        pages = self.get_pages_from_collection(section)
        # Recursively run through each page
        while len(pages) > 0:
            # Check if the current page is a media page or a collection page
            if pages[0] is None:
                # Do nothing if the page is null
                pass
            elif "url" in pages[0]:
                # Download the media page
                self.download_page(pages[0], directory)
            else:
                print("Scanning \".../" + pages[0]["page_url"] + "\"")
                # Try getting a cover image page
                cover_page = get_cover_page(pages[0])
                if cover_page not in pages:
                    pages.append(cover_page)
                # Get additional collections
                pages.extend(self.get_pages_from_collection(pages[0]["page_url"], pages[0]))
            # Delete the page once finished
            del pages[0]
        # Return True if successful
        return True
    
    def get_categories(self, beautiful_soup:bs4.BeautifulSoup) -> dict:
        """
        Returns a dictionary containing the metadata categories for a TGComics media page.
        
        :param beautiful_soup: BeautifulSoup object containing parsed TGComics web page
        :type beautiful_soup: bs4.BeautifulSoup
        :return: Dictionary containing TGComics metadata
        :rtype: dict
        """
        info = dict()
        # Get title
        entry_header = None
        try:
            entry_header = beautiful_soup.find("header", {"class":"entry-header"})
            info["title"] = entry_header.find("h1", {"itemprop":"headline"}).get_text().strip()
        except AttributeError: info["title"] = None
        # Get the author
        try:
            authors = []
            for author_element in entry_header.find_all("a", {"href":re.compile(r"\/tgc\/author\/")}):
                authors.append(author_element.get_text().strip())
            assert len(authors) > 0
            info["authors"] = authors
        except (AssertionError, AttributeError): info["authors"] = None
        # Get the artist
        try:
            artists = []
            for artist_element in entry_header.find_all("a", {"href":re.compile(r"\/tgc\/artist\/")}):
                artists.append(artist_element.get_text().strip())
            assert len(artists) > 0
            info["artists"] = artists
        except (AssertionError, AttributeError): info["artists"] = None
        # Get the age rating
        strip_regex = r"^<[^>]*>|<\s*\/[^>]*>$|<\s*strong\s*>.+<\s*\/\s*strong\s*>"
        category_elements = None
        try:
            category_elements = beautiful_soup.find("div", {"class":"omsc-toggle-inner"}).find_all("p")
            rating_element = gd_extractor.get_element_with_string(category_elements, re.compile(r"[Rr]atings:"), True)
            info["age_rating"] = re.sub(strip_regex, "", str(rating_element)).strip()
            assert rating_element is not None and not info["age_rating"] == ""
        except (AttributeError, AssertionError): info["age_rating"] = None
        # Get the genres
        try:
            genre_element = gd_extractor.get_element_with_string(category_elements, re.compile(r"[Gg]enre:"), True)
            info["genres"] = re.sub(strip_regex, "", str(genre_element)).strip()
            info["genres"] = re.sub(r"\s*,\s*", ",", info["genres"]).split(",")
            assert genre_element is not None and not info["genres"] == [""]
        except (AttributeError, AssertionError): info["genres"] = None
        # Get the sexual_preferences
        try:
            sex_element = gd_extractor.get_element_with_string(category_elements, re.compile(r"[Ss]exual\s*[Pp]references:"), True)
            info["sexual_preferences"] = re.sub(strip_regex, "", str(sex_element)).strip()
            info["sexual_preferences"] = re.sub(r"\s*,\s*", ",", info["sexual_preferences"]).split(",")
            assert sex_element is not None and not info["sexual_preferences"] == [""]
        except (AttributeError, AssertionError): info["sexual_preferences"] = None
        # Get the transformation categories
        try:
            tf_element = gd_extractor.get_element_with_string(category_elements, re.compile(r"[Tt]ransformation:"), True)
            info["transformations"] = re.sub(strip_regex, "", str(tf_element)).strip()
            info["transformations"] = re.sub(r"\s*,\s*", ",", info["transformations"]).split(",")
            assert tf_element is not None and not info["transformations"] == [""]
        except (AttributeError, AssertionError): info["transformations"] = None
        # Get the transformation details
        try:
            tf_details_element = gd_extractor.get_element_with_string(category_elements, re.compile(r"[Tt]ransformation\s*[Dd]etails:"), True)
            info["transformation_details"] = re.sub(strip_regex, "", str(tf_details_element)).strip()
            info["transformation_details"] = re.sub(r"\s*,\s*", ",", info["transformation_details"]).split(",")
            assert tf_details_element is not None and not info["transformation_details"] == [""]
        except (AttributeError, AssertionError): info["transformation_details"] = None
        # Get the completion status
        try:
            status_element = gd_extractor.get_element_with_string(category_elements, re.compile(r"[Ss]tatus:"), True)
            info["status"] = re.sub(strip_regex, "", str(status_element)).strip()
            assert status_element is not None and not info["status"] == ""
        except (AttributeError, AssertionError): info["status"] = None
        # Get the date
        try:
            time_string = beautiful_soup.find("time", {"class":"entry-time"}).get_text()
            info["date"] = gd_extractor.get_date(time_string)
        except AttributeError: info["date"] = None
        # Return the info
        return info
    
    def get_pages_from_collection(self, section:str, metadata:dict={}) -> List[dict]:
        """
        Returns a list of pages on a TGComics.com media collection page.

        :param section: Path section of a TGComics page
        :type section: str, required
        :param metadata: Existing metadata to pass use if metadata can't be found on the page
        :type metadata: dict, optional
        :return: List of dictionaries with page and metadata info
        :rtype: List[dict]
        """
        # Load the collection page
        self.initialize()
        self.cookies_to_header
        base_url = f"https://tgcomics.com/tgc/{section}/"
        bs = self.web_get(base_url)
        # Get the page section
        try:
            true_section = re.findall(self.section, bs.find("link", {"rel":"canonical"})["href"])[0]
        except IndexError: return []
        # Set the base metadata passed into the function
        base_metadata = copy.deepcopy(metadata)
        try:
            assert base_metadata["collection_description"] is not None
        except (AssertionError, KeyError): base_metadata["collection_description"] = None
        # Get the category information for the webpage
        categories = self.get_categories(bs)
        for item in categories.items():
            try:
                assert item[1] is None
                assert base_metadata[item[0]] is not None
            except (AssertionError, KeyError):
                base_metadata[item[0]] = item[1]
        # Add cover element, if applicable
        base_metadata["cover_image"] = None
        base_metadata["cover_page"] = None
        image_element = bs.find("img", {"class":"size-full", "src":re.compile(r"tgcomics\.com\/(?!site-nav)")})
        if image_element is not None:
            base_metadata["cover_image"] = image_element["src"]
            base_metadata["cover_page"] = true_section
        # Get a list of media pages in the collection
        pages = []
        link_elements = bs.find_all("div", {"class":"toctitle"})
        for link_element in link_elements:
            # Create a page dict with all the base metadata info
            page = copy.deepcopy(base_metadata)
            # Get the URL of the link element
            try:
                regex = r"(?<=\/tgc\/).+[^\/](?=\/?$)"
                page["page_url"] = re.findall(regex, link_element.find("a")["href"])[0]
            except IndexError: continue
            # Get the description of the link, if available
            parent = link_element.parent
            for i in range(0,2):
                description_element = parent.find("p", {"class":"tocexcerpt"})
                if description_element is not None:
                    description = re.sub(r"^\s*<\s*p[^>]*>\s*|\s*<\s*\/\s*p\s*>\s*$", "", str(description_element))
                    page["collection_description"] = description
                    break
                parent = parent.parent
            # Add to the list of pages
            pages.append(page)
        # Get the next page in the collection, if available
        try:
            next_link = bs.find("a", {"class":"wpv-filter-next-link"})
            next_section = re.findall(r"(?<=\/tgc\/).+$", next_link["href"])[0]
            pages.extend(self.get_pages_from_collection(next_section))
        except TypeError: pass
        # Try to get image pages if this is not a collection page
        if len(pages) == 0:
            pages = self.get_image_pages(bs, metadata)
            # Try to get video pages if this is not a collection or image page
            if len(pages) == 0:
                pages = [self.get_video_page(bs, metadata)]
            # Get archive pages as well
            pages.extend(self.get_archive_pages(bs, metadata))
        # Return pages
        return pages
    
    def get_image_pages(self, beautiful_soup:bs4.BeautifulSoup, metadata:dict={}) -> List[dict]:
        """
        Returns a list of image pages on a TGComics.com media collection page.

        :param beautiful_soup: BeautifulSoup object containing parsed TGComics web page
        :type beautiful_soup: bs4.BeautifulSoup
        :param metadata: Existing metadata to use if metadata can't be found on the page
        :type metadata: dict, optional
        :return: List of dictionaries with image page and metadata info
        :rtype: List[dict]
        """
        # Set the base metadata passed into the function
        base_metadata = copy.deepcopy(metadata)
        try:
            assert base_metadata["collection_description"] is not None
        except (AssertionError, KeyError): base_metadata["collection_description"] = None
        # Get the category information for the webpage
        categories = self.get_categories(beautiful_soup)
        for item in categories.items():
            try:
                assert item[1] is None
                assert base_metadata[item[0]] is not None
            except (AssertionError, KeyError):
                base_metadata[item[0]] = item[1]
        # Get the page url
        try:
            section = re.findall(self.section, beautiful_soup.find("link", {"rel":"canonical"})["href"])[0]
            base_metadata["page_url"] = f"https://tgcomics.com/tgc/{section}/"
        except IndexError: return []
        # Get the list of slide elements
        pages = []
        slide_elements = beautiful_soup.find_all("div", {"class":"rsSlideRoot"})
        for slide_element in slide_elements:
            # Set the page to the base page
            page = copy.deepcopy(base_metadata)
            # Remove cover details
            try:
                page.pop("cover_image")
            except KeyError: pass
            try:
                page.pop("cover_page")
            except KeyError: pass
            # Get the slide title
            slide_link = slide_element.find("a", {"class":"rsImg"})
            slide_title = slide_link.get_text().strip()
            page["title"] = f"{base_metadata['title']} [{slide_title}]"
            # Get the slide image
            page["url"] = slide_link["href"]
            page["id"] = re.findall(r"(?<=\/)[^\/]+$", page["url"])[0]
            # Get the slide description
            description = ""
            paragraphs = slide_element.find_all("p")
            for paragraph in paragraphs:
                p_text = re.sub(r"^\s*<[^>]*>|<[^>]*>\s*$", "", str(paragraph)).strip()
                description = f"{description}{p_text}"
            page["description"] = base_metadata["collection_description"]
            if not description == "":
                page["description"] = description
            # Add page to the page list
            pages.append(page)
        # Return the pages
        return pages

    def get_archive_pages(self, beautiful_soup:bs4.BeautifulSoup, metadata:dict={}) -> List[dict]:
        """
        Returns a PDF and ZIP links of a piece of TGComics media, if available.

        :param beautiful_soup: BeautifulSoup object containing parsed TGComics web page
        :type beautiful_soup: bs4.BeautifulSoup
        :param metadata: Existing metadata to use if metadata can't be found on the page
        :type metadata: dict, optional
        :return: List of dictionaries with media page and metadata info
        :rtype: List[dict]
        """
        # Set the base metadata passed into the function
        base_metadata = copy.deepcopy(metadata)
        try:
            assert base_metadata["collection_description"] is not None
        except (AssertionError, KeyError): base_metadata["collection_description"] = None
        try:
            base_metadata.pop("cover_image")
        except KeyError: pass
        try:
            base_metadata.pop("cover_page")
        except KeyError: pass
        base_metadata["description"] = base_metadata["collection_description"]
        # Get the category information for the webpage
        categories = self.get_categories(beautiful_soup)
        for item in categories.items():
            try:
                assert item[1] is None
                assert base_metadata[item[0]] is not None
            except (AssertionError, KeyError):
                base_metadata[item[0]] = item[1]
        # Get the page url
        try:
            section = re.findall(self.section, beautiful_soup.find("link", {"rel":"canonical"})["href"])[0]
            base_metadata["page_url"] = f"https://tgcomics.com/tgc/{section}/"
        except IndexError: return []
        # Get the PDF link
        pages = []
        try:
            pdf_link = beautiful_soup.find("a", {"href":re.compile(r"tgcontent\.tgcomics\.com\/.+\.pdf$")})["href"]
            pdf_page = copy.deepcopy(base_metadata)
            pdf_page["title"] = f"{base_metadata['title']} [PDF]"
            pdf_page["url"] = pdf_link
            pdf_page["id"] = re.findall(r"(?<=\/)[^\/]+$", pdf_page["url"])[0]
            pages.append(pdf_page)
        except TypeError: pass
        # Get the ZIP link
        try:
            zip_link = beautiful_soup.find("a", {"href":re.compile(r"tgcontent\.tgcomics\.com\/.+\.zip$")})["href"]
            zip_page = copy.deepcopy(base_metadata)
            zip_page["title"] = f"{base_metadata['title']} [ZIP]"
            zip_page["url"] = zip_link
            zip_page["id"] = re.findall(r"(?<=\/)[^\/]+$", zip_page["url"])[0]
            pages.append(zip_page)
        except TypeError: pass
        # Return the archive pages
        return pages
        
    
    def get_video_page(self, beautiful_soup:bs4.BeautifulSoup, metadata:dict={}) -> dict:
        """
        Returns video page info on a TGComics.com media video page.

        :param beautiful_soup: BeautifulSoup object containing parsed TGComics web page
        :type beautiful_soup: bs4.BeautifulSoup
        :param metadata: Existing metadata to use if metadata can't be found on the page
        :type metadata: dict, optional
        :return: Dictionaries with video page and metadata info
        :rtype: dict
        """
        # Set the base metadata passed into the function
        base_metadata = copy.deepcopy(metadata)
        try:
            assert base_metadata["collection_description"] is not None
        except (AssertionError, KeyError): base_metadata["collection_description"] = None
        # Get the category information for the webpage
        categories = self.get_categories(beautiful_soup)
        for item in categories.items():
            try:
                assert item[1] is None
                assert base_metadata[item[0]] is not None
            except (AssertionError, KeyError):
                base_metadata[item[0]] = item[1]
        # Get the page url
        try:
            section = re.findall(self.section, beautiful_soup.find("link", {"rel":"canonical"})["href"])[0]
            base_metadata["page_url"] = f"https://tgcomics.com/tgc/{section}/"
        except IndexError: return None
        # Remove cover details
        try:
            base_metadata.pop("cover_image")
        except KeyError: pass
        try:
            base_metadata.pop("cover_page")
        except KeyError: pass
        # Set the description
        base_metadata["description"] = base_metadata["collection_description"]
        # Get the video url
        try:
            video_element = beautiful_soup.find("video", {"id":"player"})
            video_element = video_element.find("source")
            base_metadata["url"] = video_element["src"]
            base_metadata["id"] = re.findall(r"(?<=\/)[^\/]+$", base_metadata["url"])[0]
            return base_metadata
        except AttributeError:
            return None
    
    def download_page(self, page:dict, directory:str) -> str:
        """
        Downloads a given TGComics page.
    
        :param page: Metadata dict for a given TGComics page.
        :type page: dict, required
        :param directory: Directory to save files into
        :type directory: str, required
        :return: Path of the media file created, if applicable
        :rtype: str
        """
        # Get the author/artist
        subs = []
        try:
            assert page["authors"] is not None
            subs = [page["authors"][0]]
        except (AssertionError, KeyError): pass
        try:
            assert page["artists"] is not None
            subs = [page["artists"][0]]
        except (AssertionError, KeyError): pass
        # Get the remaining subdirectory list from the page url
        section = re.findall(self.section, page["page_url"])[0]
        subs.extend(section.split("/")) 
        subs.insert(0, "tgcomics")
        # Download the page
        return super().download_page(page, directory, subs)
    
    def login(self, username:str, password:str) -> bool:
        """
        Attempts to login the requests_session object to tgcomics.com

        :param username: TGComics username
        :type username: str, required
        :param password: TGComics password
        :type password: str, required
        :return: Whether login was successful
        :rtype: bool
        """
        # Load the login page to get request verification cookies
        bs = self.web_get("https://tgcomics.com/tgc/")
        input_element = bs.find("input", {"name":"_amember_redirect_url"})    
        # Attempt login
        request = dict()
        request["amember_login"] = username
        request["amember_pass"] = password
        request["_amember_redirect_url"] = input_element["value"]
        request["wp-submit"] = "Login"
        headers = {"Content-Type":"application/x-www-form-urlencoded"}
        response = self.requests_session.post("https://tgcomics.com/member/login", headers=headers, data=request)
        # Move to main TGComics page
        self.cookies_to_header()
        bs = self.web_get("https://tgcomics.com/tgc/")
        # Check whether login was successful
        member_link = bs.find("a", {"href":re.compile(r"\/member\/member")})
        self.attempted_login = True
        return member_link is not None

    def user_login(self) -> bool:
        """
        Asks user for TGComics.com login information before attempting login.
        """
        super().user_login("TGComics")
