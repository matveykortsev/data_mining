# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
DB_NAME = 'insta'


class InstaparserPipeline:

    def __init__(self):
        self.followings = []
        self.followers = []
        self.mongo_client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
        self.db = self.mongo_client[DB_NAME]

    def process_item(self, item, spider):
        followers = item.get('followers', None)
        followings = item.get('followings', None)
        if followers:
            try:
                self.db.get_collection(spider.name).update_one(
                    {'user_id': item['user_id'], 'username': item['username']},
                    {'$push': {'followers': {'$each': item['followers']}}},
                    upsert=True
                )
            except Exception as e:
                print(e)
        elif followings:
            try:
                self.db.get_collection(spider.name).update_one(
                    {'user_id': item['user_id'], 'username': item['username']},
                    {'$push': {'followings': {'$each': item['followings']}}},
                    upsert=True
                )
            except Exception as e:
                print(e)
        print()
        return item
