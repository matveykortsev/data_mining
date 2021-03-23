from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from booksparser.spiders.book24 import Book24Spider
from booksparser.spiders.labirint import LabirintSpider
from booksparser import settings

if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    # TODO parseargv for mark's
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(Book24Spider, mark='глуховский')
    process.crawl(LabirintSpider, mark='глуховский')
    process.start()