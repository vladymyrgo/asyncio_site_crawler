# asyncio_site_crawler

Simple site crawler to find all site pages or to download exact pages.

Two classes founded
  - Crawler() - to crawl all site by domain.
  - PagesDownloader() - to download pages.

Requirements (requirements.txt):
  - pip install aiohttp
  - pip install lxml

### Crawler example:
```
# Custom page handler for each page.
def my_page_handler(url, dom):
    clean_page = dom.text_content()
    page = MyPage(url=url, body=clean_page)

crawler = Crawler('the-site.com', workers=7, page_handler=my_page_handler)
crawler.crawl()
```

### PagesDownloader example:
```
# Custom page handler for each page.
def my_page_handler(url, dom):
    clean_page = dom.text_content()
    page = MyPage(url=url, body=clean_page)

sites = ['first-site.com', 'other-site.com']
downloader = PagesDownloader(urls=sites, workers=7, page_handler=my_page_handler)
downloader.download_pages()
```
