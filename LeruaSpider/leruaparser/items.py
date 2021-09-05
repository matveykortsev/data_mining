# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst


def get_values(value):
    return value.strip()


class LeruaparserItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    characteristics_keys = scrapy.Field()
    characteristics_values = scrapy.Field(output_processor=MapCompose(get_values))
    characteristics = scrapy.Field()
