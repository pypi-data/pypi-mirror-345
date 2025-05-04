import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from src.link_thief.link_thief import crawl_page, crawl_list, crawl_sitemap, crawl_sitemaps_from_website, crawl_website, filter_by_type, LinkType


def test_crawl_page_not_url():
    urls = crawl_page("some")
    print(urls)
    assert len(urls) == 0

def test_crawl_page_total():
    urls = crawl_page("http://localhost:8000/scrapable/1/")
    print(urls)
    assert len(urls) == 10

def test_crawl_page_internal():
    urls = crawl_page("http://localhost:8000/scrapable/1/")
    internal_urls = []
    for url in urls:
        if url.type == LinkType.INTERNAL:
            internal_urls.append(url)

    assert len(internal_urls) == 8

def test_crawl_page_external():
    urls = crawl_page("http://localhost:8000/scrapable/1/")
    external_urls = []
    for url in urls:
        if url.type == LinkType.EXTERNAL:
            external_urls.append(url)
    assert len(external_urls) == 2

def test_crawl_list_pages():
    urls = crawl_list(["http://localhost:8000/scrapable/1/","http://localhost:8000/scrapable/2/"], crawl_page)
    assert len(urls) == 17

def test_crawl_list_sitemaps():
    urls = crawl_list(["http://localhost:8000/sitemap-static1.xml","http://localhost:8000/sitemap-static2.xml"], crawl_sitemap)
    assert len(urls) == 7

def test_crawl_sitemap_single():
    urls = crawl_sitemap("http://localhost:8000/sitemap-static1.xml")
    assert len(urls) == 3

def test_crawl_sitemap_single_wrong():
    urls = crawl_sitemap("http://localhost:8000/sitemap-static5.xml")
    assert len(urls) == 0

def test_crawl_sitemap_all_with_index():
    urls = crawl_sitemap("http://localhost:8000/sitemap.xml")
    print(urls)
    assert len(urls) == 7

def test_crawl_sitemap_from_website_url():
    urls = crawl_sitemaps_from_website("http://localhost:8000")
    print(urls)
    assert (len(urls)) == 6

def test_crawl_whole_website_total():
    links = crawl_website("http://127.0.0.1:8000")
    print(links)
    assert len(links) == 45

def test_crawl_whole_website_total_internal():
    links = crawl_website("http://127.0.0.1:8000")
    assert len(filter_by_type(links, LinkType.INTERNAL)) == 24

def test_crawl_whole_website_total_externale():
    links = crawl_website("http://127.0.0.1:8000")
    assert len(filter_by_type(links, LinkType.EXTERNAL)) == 21