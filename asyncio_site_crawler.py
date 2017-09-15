#!/usr/bin/env python3
import re
import aiohttp
import asyncio
from lxml.html import fromstring


class Crawler():
    """root_url - (Str) Site url
    workerts - (Int) Amount of async workers. Default is 10
    page_handler - is a function to handle each page of the site.
    Must have two atrs: (url, dom)
    Example:
    ```
    def my_page_handler(url, dom):
        clean_page = dom.text_content()
        page = MyPage(url=url, body=clean_page)

    crawler = Crawler('site.com', workers=7, page_handler=my_page_handler)
    crawler.crawl()
    ```
    """

    def __init__(self, root_url, workers=10, page_handler=None):
        self.workers = workers
        self.page_handler = page_handler
        self.root_url = root_url
        self.crawled_urls = set()
        self.founded_urls = set([self.root_url])
        self.url_hub = [self.root_url]
        self.allowed_regex = '\.((?!htm)(?!php)\w+)$'

        self.queue = asyncio.Queue()
        self.queue.put_nowait(self.root_url)

    @asyncio.coroutine
    def handle_task(self):
        while True:
            queue_url = yield from self.queue.get()
            self.crawled_urls.update([queue_url])
            response = yield from aiohttp.request('GET', queue_url)
            if response.status == 200:
                body = yield from response.text()
                dom = fromstring(body)

                if self.page_handler:
                    self.page_handler(queue_url, dom)

                self.add_new_urls_to_queue(dom=dom)

            if self.queue.empty():
                break

    def add_new_urls_to_queue(self, dom):
        dom.make_links_absolute(self.root_url)
        for l in dom.iterlinks():
            newurl = l[2]
            if l[0].tag == 'a' and self.is_valid(newurl):
                if '#' in newurl:
                    newurl = newurl[:newurl.find('#')]
                self.founded_urls.update([newurl])
                self.queue.put_nowait(newurl)

    def is_valid(self, url):
            if '#' in url:
                url = url[:url.find('#')]
            if url in self.founded_urls:
                return False
            if url in self.crawled_urls:
                return False
            if self.root_url not in url:
                return False
            if re.search(self.regex, url):
                return False
            return True

    def crawl(self):
        self.regex = re.compile(self.allowed_regex)

        loop = asyncio.get_event_loop()

        tasks = [self.handle_task() for i in range(self.workers)]
        loop.run_until_complete(asyncio.wait(tasks))


class PagesDownloader():
    """urls - List of urls to download
    workerts - (Int) Amount of async workers. Default is 10
    page_handler - is a function to handle each page.
    Must have two atrs: (url, dom)
    Example:
    ```
    def my_page_handler(url, dom):
        clean_page = dom.text_content()
        page = MyPage(url=url, body=clean_page)

    sites = ['site.com', 'other-site.com']
    downloader = PagesDownloader(urls=sites, workers=7, page_handler=my_page_handler)
    downloader.download_pages()
    ```
    """

    def __init__(self, urls, workers=10, page_handler=None):
        workers = workers
        self.page_handler = page_handler

        self.sem = asyncio.Semaphore(workers)
        self.urls = urls

    @asyncio.coroutine
    def download_page(self, url):
        with (yield from self.sem):
            response = yield from aiohttp.request('GET', url)
            if response.status == 200:
                body = yield from response.text()
                dom = fromstring(body)

                if self.page_handler:
                    self.page_handler(queue_url, dom)

    def download_pages(self):
        loop = asyncio.get_event_loop()
        f = asyncio.wait([self.download_page(url) for url in self.urls])
        loop.run_until_complete(f)
