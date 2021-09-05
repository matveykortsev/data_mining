import scrapy
from scrapy.http import HtmlResponse
from bookparser.bookparser.items import BookparserItem


class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']

    def __init__(self, mark, **kwargs):
        super().__init__(*kwargs)
        self.start_urls = [f'https://book24.ru/search/?q={mark}']

    def parse(self, response: HtmlResponse, **kwargs):
        books_links = response.xpath('//a[contains(@class,"book-preview__image-link")]//@href').getall()
        for link in books_links:
            yield response.follow(link, callback=self.parse_books)
        next_page = response.xpath('//a[contains(@class,"catalog-pagination__item _text")]//@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_books(self, response: HtmlResponse):
        link = response.url
        rating = response.xpath('//div[contains(@class,"live-lib__rate-value")]/text()').get()
        title = response.xpath('//div[contains(@class,"item-detail__informations-box")]/h1/text()').getall()
        authors = response.xpath('//a[@itemprop="author"]//text()').get()
        price_old = response.xpath('//div[contains(@class,"item-actions__price-old")]//text()').get()
        price_actual = response.xpath('//b[@itemprop="price"]/text()').get()
        yield BookparserItem(link=link, title=title, authors=authors,
                              price_old=price_old, price_actual=price_actual,
                              rating=rating)