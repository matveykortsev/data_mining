from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from instaparser.spiders.instagram import InstagramSpider
from instaparser import settings
from pymongo import MongoClient

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
DB_NAME = 'insta'


def search_followings(user):
    with MongoClient(host=MONGO_HOST, port=MONGO_PORT) as client:
        db = client[DB_NAME]
        followings = db.get_collection('instagram').find_one({'username': user}, projection={'followings': 1, '_id': 0})
    return followings['followings']

def search_followers(user):
    with MongoClient(host=MONGO_HOST, port=MONGO_PORT) as client:
        db = client[DB_NAME]
        followers = db.get_collection('instagram').find_one({'username': user}, projection={'followers': 1, '_id': 0})
    return followers['followers']

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    users_to_scrape = input('Type users to scrape (via space separator): ').split()
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstagramSpider, users_to_scrape=users_to_scrape)
    search_followings(user='ai_machine_learning')
    search_followers(user='ai_machine_learning')

    process.start()