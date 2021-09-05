# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
DB_NAME = 'books'


class BookparserPipeline:
    def __init__(self):
        self.mongo_client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
        self.db = self.mongo_client[DB_NAME]

    def process_item(self, item, spider):
        if not item['price_old']:
            item['price_old'] = None
        item['title'] = item['title'][0].strip()
        item['price_old'] = item['price_old'][:-3]
        self.db.get_collection(spider.name).update_one({'link': item['link']}, {'$set': item}, upsert=True)
        return item
