import scrapy
from scrapy.http import HtmlResponse
from leruaparser.items import LeruaparserItem
from scrapy.loader import ItemLoader


class LeruaSpider(scrapy.Spider):
    name = 'lerua'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, mark, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://leroymerlin.ru/search/?q={mark}']


    def parse(self, response: HtmlResponse):
        item_links = response.xpath('//a[contains(@class,"plp-item__info__title")]//@href').getall()
        for link in item_links:
            yield response.follow(link, callback=self.parse_item)

    def parse_item(self, response: HtmlResponse):
        loader = ItemLoader(item=LeruaparserItem(), response=response)
        loader.add_xpath('title', '//h1/text()')
        loader.add_value('link', response.url)
        loader.add_xpath('price', '//span[@slot="price"]/text()')
        loader.add_xpath('photos', '//picture[@slot="pictures"]/source[contains(@media," only screen and (min-width: 1024px)")]/@srcset')
        loader.add_xpath('characteristics_keys', '//dt/text()')
        loader.add_xpath('characteristics_values', '//dd/text()')
        yield loader.load_item()

