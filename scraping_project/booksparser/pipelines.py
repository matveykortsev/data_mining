# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from booksparser.items import BooksparserItem, LabirintItem
from pymongo import MongoClient
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
DB_NAME = 'books'

class BooksparserPipeline(object):
    def __init__(self):
        self.mongo_client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
        self.db = self.mongo_client[DB_NAME]

    def process_item(self, item, spider):
        if isinstance(item, BooksparserItem):
            return self.process_books24(item, spider)
        if isinstance(item, LabirintItem):
            return self.process_labirint(item, spider)

    def process_labirint(self, item, spider):
        if not item['price'] and not item['price_actual'] and not item['price_old']:
            item['price'] = 'Out of stock'
            del item['price_old']
            del item['price_actual']
        elif item['price']:
            del item['price_old']
            del item['price_actual']
        else:
            del item['price']
        self.db.get_collection(spider.name).update_one({'link': item['link']}, {'$set': item}, upsert=True)
        return item

    def process_books24(self, item, spider):
        try:
            item['price_old'] = item['price_old'][:-3]
        except TypeError:
            del item['price_old']
        item['title'] = item['title'][0].strip()
        self.db.get_collection(spider.name).update_one({'link': item['link']}, {'$set': item}, upsert=True)
        return item
