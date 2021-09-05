import requests
import time
from pymongo import MongoClient
from lxml import html
from datetime import datetime

HOST = '127.0.0.1'
PORT = 27017
DB_NAME = 'news'
COLLECTION_NAME = 'daily_news'
URL = 'https://yandex.ru/news/'
#URL = 'https://lenta.ru/'
#URL = 'https://news.mail.ru/'
USER_AGENT = user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru-RU) AppleWebKit/533.18.1 (KHTML, like Gecko) Version/5.0.2 Safari/533.18.5'
# XPATH_STRING_MAIL = '//table[contains(@class,"daynews__inner")]//td[position() <= 2]/div[contains(@class,"daynews__item")]'
# XPATH_STRING_LENTA = '//div[contains(@class, "-yellow-box__wrap")]//*[contains(@class, "item")]'
XPATH_STRING = '//*[contains(@class,"news-top-flexible-stories")]//*[contains(@class,"mg-grid__col")]'


class NewsParser:
    def __init__(self, urls, sleep, user_agent, retry_number=1, proxies=None):
        self.start_url = urls
        self.retry_number = retry_number
        self.sleep = sleep
        self.headers = {
            'User-Agent': user_agent
        }
        self.proxies = proxies

    def _get(self, *args, **kwargs):
        for i in range(self.retry_number):
            response = requests.get(*args, **kwargs)
            if response.ok:
                return response
            else:
                response.raise_for_status()
                time.sleep(self.sleep)
                print('Trying again...')
                continue

    def _run(self, url):
        r = self._get(url, headers=self.headers, proxies=self.proxies)
        return r

    def get_news(self, xpath_string):
        response = self._run(self.start_url)
        page = html.fromstring(response.text)
        news = page.xpath(xpath_string)
        return news

    @staticmethod
    def get_value(elems):
        if elems:
            return elems[0]
        return None

    def parse_mail_data(self, elem):
        news_info = {}
        link = self.get_value(elem.xpath('.//@href'))
        response = self._run(url=link)
        news_page = html.fromstring(response.text)
        publication_date = self.get_value(news_page.xpath('//*[contains(@class,"breadcrumbs__item")][1]//@datetime'))
        source_link = self.get_value(news_page.xpath('//*[contains(@class,"breadcrumbs__item")][2]//*[contains(@class, "breadcrumbs__link")]/@href'))
        source = self.get_value(news_page.xpath('//*[contains(@class,"breadcrumbs__item")][2]//*[contains(@class, "link__text")]/text()'))
        news_info['news_title'] = self.get_value(elem.xpath('.//*[contains(@class,"photo__title")]/text()'))
        news_info['link'] = link
        news_info['publication_date'] = publication_date
        news_info['source'] = source
        news_info['source_link'] = source_link
        return news_info

    def parse_lenta_data(self, elem):
        news_info = {}
        link = URL + self.get_value(elem.xpath('.//@href'))
        response = self._run(url=link)
        news_page = html.fromstring(response.text)
        publication_date = self.get_value(news_page.xpath('//*[contains(@class,"b-topic__info")]//@datetime'))
        news_info['news_title'] = self.get_value(elem.xpath('.//text()'))
        news_info['link'] = link
        news_info['publication_date'] = publication_date
        news_info['source'] = 'Lenta.ru'
        news_info['source_link'] = None
        return news_info

    def parse_yandex_data(self, elem):
        news_info = {}
        date_now = str(datetime.now().date())
        publication_date = date_now + 'T' + self.get_value(elem.xpath('//*[contains(@class,"mg-card-source__time")]//text()'))
        news_info['news_title'] = self.get_value(elem.xpath('.//*[contains(@class,"mg-card__title")]//text()'))
        news_info['link'] = self.get_value(elem.xpath('//*[contains(@class,"mg-card__link")]//@href'))
        news_info['publication_date'] = publication_date
        news_info['source'] = self.get_value(elem.xpath('.//*[contains(@class,"mg-card__source-link")]//text()'))
        return news_info

    @staticmethod
    def save_to_mongo(object, db_name, collection_name, host=None, port=None):
        with MongoClient(host=host, port=port) as mongo_client:
            db = mongo_client[db_name]
            db.get_collection(collection_name).update_many(object, upsert=True)


if __name__ == '__main__':
    result_list = []
    parser = NewsParser(urls=URL, sleep=1, user_agent=USER_AGENT)
    news = parser.get_news(XPATH_STRING)
    for elem in news:
        news_info = parser.parse_yandex_data(elem)
        result_list.append(news_info)
    parser.save_to_mongo(result_list, db_name=DB_NAME, collection_name=COLLECTION_NAME, host=HOST, port=PORT)
    print(result_list)
