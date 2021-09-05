# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.misc import md5sum
from leruaparser.items import LeruaparserItem
from pymongo import MongoClient

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
DB_NAME = 'lerua'


class LeruaImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item["photos"]:
            for photo_url in item['photos']:
                try:
                    yield scrapy.Request(photo_url, meta={'title': item['title']})
                except Exception as e:
                    print(e)

    def image_downloaded(self, response, request, info):
        checksum = None
        for path, image, buf in self.get_images(response, request, info):
            if checksum is None:
                buf.seek(0)
                checksum = md5sum(buf)
            width, height = image.size
            folder = response.meta['title']
            path = f'{folder}/{checksum}.jpg'
            self.store.persist_file(
                path, buf, info,
                meta={'width': width, 'height': height},
                headers={'Content-Type': 'image/jpeg'})
        return checksum

    def item_completed(self, results, item, info):
        if results:
            item["photos"] = [itm[1] for itm in results]
        print()
        return item


class LeruaparserPipeline:
    def __init__(self):
        self.mongo_client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
        self.db = self.mongo_client[DB_NAME]

    def process_item(self, item, spider):
        characteristics = {}
        for key, value in zip(item['characteristics_keys'], item['characteristics_values']):
            characteristics.update({key: value})
        item['characteristics'] = characteristics
        del item['characteristics_values']
        del item['characteristics_keys']
        self.db.get_collection(spider.name).update_one({'link': item['link']}, {'$set': item}, upsert=True)
        return item
