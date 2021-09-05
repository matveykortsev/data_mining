from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from bookparser.spiders.book24 import Book24Spider
from bookparser.bookparser import settings

if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(Book24Spider, mark='глуховский')

    process.start()