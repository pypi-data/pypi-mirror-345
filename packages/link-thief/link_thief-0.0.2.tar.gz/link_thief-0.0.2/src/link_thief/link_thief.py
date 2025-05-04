import re
from urllib.parse import urlparse, urlunparse
from urllib.robotparser import RobotFileParser
from enum import Enum
import concurrent.futures as fu
from concurrent.futures import ThreadPoolExecutor, Future

import requests
from bs4 import BeautifulSoup

url_valid_pattern = re.compile(
    r"^(?:http|ftp)s?://"
    r"(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?$)"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$", re.IGNORECASE)

HEADERS={
    "User-Agent" :	"Mozilla/5.0 (X11; Linux x86_64; rv:104.0) Gecko/20100101 Firefox/104.0",
    "Accept": "text/html,application/xhtml+xml,application/xml",
    "Referer": "https://google.com"
}

class LinkType(Enum):
    """
    Types of links supported
    """
    INTERNAL = 1
    EXTERNAL = 2

class Url:
    """
    Wrapper around an usual string representing a URL address
    ...
    Attributes
    __________
    href: str
        An actual reference 
    type: LinkType
        Type of reference
    anchor: str
        Text wrapped around <a> tag
    crawlable: bool
        Can this link be crawled by this crawler
    """
    def __init__(self, href: str = "", type: LinkType = LinkType.INTERNAL, anchor: str = "", crawlable: bool = False):  
        self.href = href
        self.type = type
        self.anchor = anchor
        self.crawlable = crawlable 


def _is_valid_url(url: str, pattern=url_valid_pattern) -> bool:
    """
    Check whether the URL is valid or not.
    ...
    Attributes
    __________
    url: str
        An actual address
    
    Return
    _______
    bool: bool
        Return a status of the page, valid this page or not
    """
    return re.match(pattern, url) is not None 

def _crawlable(url: str) -> bool:
    """
    Check if the provided URL is crawlable
    ...
    Attributes
    __________
    url: str
        An URL to check

    Return
    ______
    bool: bool
        Return a status of page and the crawlable this page or not

    """
    notcrawlable_ext = (
        ".zip",
        ".mp4",
        ".mp3",
        ".js",
        ".css",
        ".tar",
        ".7z",
        ".png",
        ".jpg",
        ".webp",
        ".svg",
        ".gz",
        ".ico",
        ".pdf",
        ".fp2",
        ".epub",
        ".txt",
    )
    if url.endswith(notcrawlable_ext):
        return False
    return True

def _get_page(url: str | Url) -> tuple[int, str]:
    """
        To scrape the content of a webpage
        ...
        Attributes
        __________
        url: str | Url
            A URL to scrape the content from

        Returns
        _______
        tuple: tuple[int,str]
            A tuple of the status code of the response (500 if an error occurred) and the content of the response
    """
    if hasattr(url, 'href'):
        in_work_url = url.href
    else:
        in_work_url = url


    try:
        response = requests.get(in_work_url, headers=HEADERS, timeout=10)
        return (response.status_code, response.text)
    except:
        return (500, "")

def _remove_duplicates(urls: list[Url]) -> list[Url]:
    """
        Removing duplicates from the provided list by removing the first occurrence
        ...
        Attributes
        __________
        urls: list[Url]
            A list of Url-class objects

        Returns
        _______
            A cleaned list of Url-class objects
    """
    only_urls = []
    for url in urls:
        only_urls.append(url.href)
    
    only_urls = list(set(only_urls))
    
    new_urls = []
    for url in only_urls:
        for full_url in urls:
            if full_url.href == url and full_url not in new_urls:
                new_urls.append(full_url)
                break

    return new_urls

def crawl_sitemap(url: str | Url) -> list[Url]:
    """
    Recursively crawl through the sitemap
    ...
    Attributes
    __________
    url: str | Url
        url of sitemap
    
    Returns
    _______
        A list of Url-class objects with sitemap URLs in it
    """
    links = []
    status_code, page = _get_page(url)
    if status_code == 200:
        soup = BeautifulSoup(page, 'xml')
        for sitemap in soup.find_all('sitemap'):
            loc = sitemap.find('loc')
            if loc:
                links += crawl_sitemap(loc.text)
        for url_in_sitemap in soup.find_all('url'):
            loc = url_in_sitemap.find('loc')
            if loc:
                links.append(Url(
                    href=loc.text.replace(url, ""),
                    type=LinkType.INTERNAL,
                    anchor=None,
                    crawlable=True
                ))

    return links

def crawl_page(url: str | Url) -> list[Url]:
    """
    Crawl a page and gather all links in there
    ...
    Attributes
    __________
    url: str | Url
        An webpage address to scrape links from
    
    Returns
    _______
        A list of Url-class objects with links
    """
    url_parsed = urlparse(url)
    url_deparsed = urlunparse([url_parsed.scheme, url_parsed.netloc, '', '', '', ''])
    links = []
    status_code, page = _get_page(url)
    if status_code == 200:
        soup = BeautifulSoup(page, 'lxml')
        for link in soup.find_all("a"):
            # Does our link even has 'href' attribute and it is not 'anchor' link
            if link.has_attr('href') and "#" not in link['href']:
                # We check again, on does it crawlable to deserve a chanse to 
                # be inserted indo database
                if _crawlable(link["href"]):
                    if link['href'].startswith(('/')):
                        links.append(Url(
                            href=urlunparse([url_parsed.scheme, url_parsed.netloc, link['href'], '', '', '']),
                            anchor=link.text,
                            type=LinkType.INTERNAL,
                            crawlable=True
                        ))
                    else:
                        if link['href'].startswith((url_deparsed, url_deparsed.replace("https", "http"), url_deparsed.replace("http", "https"))):
                            links.append(Url(
                                href=link['href'].replace(url_deparsed, ""),
                                anchor=link.text,
                                type=LinkType.INTERNAL,
                                crawlable=True
                            ))
                        else:
                            links.append(Url(
                                href=link['href'],
                                anchor=link.text,
                                type=LinkType.EXTERNAL,
                                crawlable=True
                            ))
                else:
                    links.append(Url(
                        href=link['href'],
                        anchor=link.text,
                        type=LinkType.INTERNAL,
                        crawlable=False
                    ))

    return links

def crawl_list(urls: list[str] | list[Url], scraper) -> list[Url]:
    """
    Crawl a list of pages in parallel
    ...
    Attributes
    __________
    urls: list[str] | list[Url]
        A list of webpages to crawl
    scraper:
        A callable to use for scraping in parallel must accept one attribute, either url or Url

    Returns
    _______
        A list of Url-class objects
    """
    links = []
    pool: list[Future] = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for url in urls:
            pool.append(executor.submit(scraper, url))
        
        for process in  fu.as_completed(pool):
            links += process.result()
    
    return links

def crawl_sitemaps_from_website(entry_website_url: str) -> list[Url]:
    """
    Crawl sitemaps through the website entry point; no need to specify the sitemap URL.
    ...
    Attributes
    __________
    entry_website_url: str
        An entry website URL to start a sitemap crawl
    
    Returns
    _______
        A list of Url-class objects
    """
    urls = []
    url_parsed = urlparse(entry_website_url)
    if _is_valid_url(entry_website_url) or url_parsed.netloc.startswith(("localhost", "127.0.0.1")):
        sitemaps = []
        robots_url = urlunparse([url_parsed.scheme, url_parsed.netloc, "robots.txt", "", "", ""])
        sitemaps_parser = RobotFileParser()
        sitemaps_parser.set_url(robots_url)
        sitemaps_parser.read()
        if sitemaps_parser.site_maps():
            sitemaps = sitemaps_parser.site_maps()
        sitemaps.append(urlunparse([url_parsed.scheme, url_parsed.netloc, "sitemap.xml", "", "", ""]))
        sitemaps.append(urlunparse([url_parsed.scheme, url_parsed.netloc, "sitemap", "", "", ""]))
        sitemaps = list(set(sitemaps))
        urls = _remove_duplicates(crawl_list(sitemaps, crawl_sitemap))
    return urls
    
def filter_by_type(urls: list[Url], type: LinkType) -> list[Url]:
    """
    To filter the URL class list by type of links in it
    ...
    Attributes
    __________
    urls: list[Url]
        A list of urls to filter
    type: LinkType
        Type of link to return
    
    Returns
    _______
        It will return a list of URLs by LinkType
    """
    urls_by_type = []
    for url in urls:
        if url.type == type:
            urls_by_type.append(url)
    
    return urls_by_type

def crawl_website(entry_website_url: str) -> list[Url]:
    """
    To crawl and obtain all links on the website
    ...
    Attributes
    __________
    entry_website_url: str
        An entry website URL to start the crawling process with
    
    Returns
    _______
        List of all links on the website
    """
    links = []
    internal_urls = []
    urls = crawl_sitemaps_from_website(entry_website_url)
    url_parsed = urlparse(entry_website_url)
    if _is_valid_url(entry_website_url) or url_parsed.netloc.startswith(("localhost", "127.0.0.1")):
        urls += crawl_page(urlunparse([url_parsed.scheme, url_parsed.netloc, "/scrapable/1/", "", "", ""]))
        urls = _remove_duplicates(urls)
        current = 0
        current_cycle_links = []
        for url in urls:
            if url.type == LinkType.INTERNAL and url.crawlable:
                internal_urls.append(url)

        while True:
            for url in current_cycle_links:
                if url.type == LinkType.INTERNAL and url not in internal_urls and url.crawlable:
                    internal_urls.append(url)
            internal_urls = _remove_duplicates(internal_urls)

            length = len(internal_urls)

            for url in internal_urls[current:]:
                current_cycle_links += crawl_page(url.href)

            if current == length:
                break

            current = length
    
    clean_urls = []
    for url in internal_urls:
        clean_urls.append(url.href)

    links = crawl_list(clean_urls, crawl_page)

    return links