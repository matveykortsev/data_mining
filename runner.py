from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess

from leruaparser import settings
from leruaparser.spiders.lerua import LeruaSpider


if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    search = 'abc'
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeruaSpider, mark=search)

    process.start()
