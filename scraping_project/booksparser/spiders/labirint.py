import scrapy
from scrapy.http import HtmlResponse
from booksparser.items import LabirintItem


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = ['http://labirint.ru/']

    def __init__(self, mark, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'http://labirint.ru/search/{mark}/']

    def parse(self, response: HtmlResponse, **kwargs):
        books_links = response.xpath('//a[@class="cover"]/@href').getall()
        for link in books_links:
            yield response.follow(link, callback=self.parse_books)
        next_page = response.xpath('//a[contains(@class,"pagination-next__text")]').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        pass

    def parse_books(self, response: HtmlResponse):
        link = response.url
        rating = response.xpath('//div[@id="rate"]/text()').get()
        title = response.xpath('//div[@id="product-title"]/h1/text()').get()
        authors = response.xpath('//div[contains(@class,"authors")]/a/text()').get()
        price = response.xpath('//span[contains(@class,"buying-price-val-number")]/text()').get()
        price_old = response.xpath('//span[contains(@class,"buying-priceold-val-number")]/text()').get()
        price_actual = response.xpath('//span[contains(@class,"buying-pricenew-val-number")]/text()').get()
        yield LabirintItem(link=link, title=title, price=price, authors=authors,
                              price_old=price_old, price_actual=price_actual,
                              rating=rating)

