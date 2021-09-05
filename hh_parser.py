from bs4 import BeautifulSoup as bs
import requests
import json
import time
from pandas import DataFrame
from pymongo import MongoClient

HOST = '127.0.0.1'
PORT = 27017
DB_NAME = 'vacancies'
START_URL = "https://hh.ru/search/vacancy"
USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru-RU) AppleWebKit/533.18.1 (KHTML, like Gecko) Version/5.0.2 Safari/533.18.5'


class HhParser:
    def __init__(self, start_url, sleep, key_word, user_agent, retry_number=1, proxies=None):
        self.start_url = start_url
        self.retry_number = retry_number
        self.sleep = sleep
        self.params = {
            'text': key_word
        }
        self.headers = {
            'User-Agent': user_agent
        }
        self.proxies = proxies

    def _get(self, *args, **kwargs):
        for i in range(self.retry_number):
            response = requests.get(*args, **kwargs)
            if response.status_code == 200:
                return response
            else:
                response.raise_for_status()
                time.sleep(self.sleep)
                print('Trying again...')
                continue

    def _run(self):
        r = self._get(self.start_url, headers=self.headers, params=self.params, proxies=self.proxies)
        return r

    def parse(self):
        vacancies = []
        is_last_page = True
        page_counter = 0
        while is_last_page:
            self.params['page'] = page_counter
            print(f'Parsing page {page_counter + 1}...')
            response = self._run()
            soap = bs(response.text, 'html.parser')
            vacancies_info = soap.findAll(attrs={'class': 'vacancy-serp-item'})
            for vacancy in vacancies_info:
                vacancy_summary = {}
                vacancy_title = vacancy.find(
                    attrs={'class': 'bloko-link HH-LinkModifier HH-VacancyActivityAnalytics-Vacancy'}).text
                vacancy_link = \
                    vacancy.find(attrs={'class': 'bloko-link HH-LinkModifier HH-VacancyActivityAnalytics-Vacancy'})[
                        'href']
                vacancy_location = vacancy.find(attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text
                vacancy_publication_date = vacancy.find(attrs={
                    'class': 'vacancy-serp-item__publication-date vacancy-serp-item__publication-date_s-only'}).text
                is_salary_provided = vacancy.find(attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
                is_employer_provided = vacancy.find(attrs={'data-qa': 'vacancy-serp__vacancy-employer'})
                if is_employer_provided:
                    vacancy_summary['employer'] = is_employer_provided.text
                else:
                    vacancy_summary['employer'] = None
                vacancy_summary['vacancy'] = vacancy_title
                vacancy_summary['link'] = vacancy_link
                vacancy_summary['location'] = vacancy_location
                vacancy_summary['publication_date'] = vacancy_publication_date
                if is_salary_provided:
                    salary = is_salary_provided.text
                    if 'от' or 'до' in salary:
                        salary = salary.split()
                        if 'от' in salary:
                            vacancy_summary['min_salary'] = ''.join(salary[1:3])
                            vacancy_summary['max_salary'] = None
                        else:
                            vacancy_summary['max_salary'] = ''.join(salary[1:3])
                            vacancy_summary['min_salary'] = None
                        vacancy_summary['currency'] = salary[-1]
                    else:
                        salary = salary.split(sep='-')
                        min_salary = ''.join(salary[0].split())
                        max_salary = ''.join(salary[1].split()[0:2])
                        currency = salary[-1].split()[-1]
                        vacancy_summary['min_salary'] = min_salary
                        vacancy_summary['max_salary'] = max_salary
                        vacancy_summary['currency'] = currency
                else:
                    vacancy_summary['min_salary'] = None
                    vacancy_summary['max_salary'] = None
                    vacancy_summary['currency'] = None
                vacancies.append(vacancy_summary)

            is_last_page = soap.find(attrs={'class': 'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})
            page_counter += 1
        print('Parsing finished')
        print(f'Total vacancies found {len(vacancies)}' + '\n')
        return vacancies

    @staticmethod
    def save_to_json(object, path):
        with open(path, 'w') as f:
            json.dump(object, f, indent=2, ensure_ascii=False)

    @staticmethod
    def save_to_csv(object, path):
        frame = DataFrame.from_records(object)
        frame.to_csv(path_or_buf=path, index=True)

    @staticmethod
    def save_to_mongo(object, db_name, collection_name, host=None, port=None):
        with MongoClient(host=host, port=port) as mongo_client:
            db = mongo_client[db_name]
            db.get_collection(collection_name).insert_many(object)

    @staticmethod
    def mongo_find(db_name, collection_name, host=None, port=None):
        choice = int(input('1. Find vacancies with salary more than limit. \n'
                           '2. Find vacancies without salary specified.'))
        with MongoClient(host=host, port=port) as mongo_client:
            db = mongo_client[db_name]
            if choice == 1:
                salary = input('Type salary limit from: ')
                result = db.get_collection(collection_name).find({
                                                'min_salary': {'$gt': f'{salary}'},
                                                'max_salary': {'$gt': f'{salary}'}
                                                })
            if choice == 2:
                result = db.get_collection(collection_name).find({'min_salary': None, 'max_salary': None})
        for vacancy in result:
            print(vacancy)

    @staticmethod
    def save_to_mongo_unique(object, db_name, collection_name, host=None, port=None):
        save_counter = 0
        with MongoClient(host=host, port=port) as mongo_client:
            db = mongo_client[db_name]
            for vacancy in object:
                db.get_collection(collection_name).update_one(vacancy, upsert=True)
                save_counter += 1
        print(f'Saved {save_counter} new vacancies')


if __name__ == "__main__":
    key_word = input('Type keyword to search: ')
    retry_number = int(input('Type number of reconnects:'))
    parser = HhParser(START_URL, 3, key_word, user_agent=USER_AGENT, retry_number=retry_number)
    result = parser.parse()
    choice = int(input('Type 1 to save via CSV \n'
                       'Type 2 to save via JSON \n'
                       'Type 3 to save into MongoDB \n'
                       'Type 4 to save new vacancies in MongoDB'))
    if choice == 1:
        path = input('Type path to save data set: ')
        parser.save_to_csv(result, path)
        print(f'Saved to {path}')
    elif choice == 2:
        parser.save_to_json(result, 'result.json')
        print('Saved to result.json')
    elif choice == 3:
        collection_name = input('Type collection name to save: ')
        parser.save_to_mongo(result, DB_NAME, collection_name, host=HOST, port=PORT)
        print(f'Saved to {collection_name} collection in database {DB_NAME}')
    elif choice == 4:
        collection_name = input('Type collection name to add vacancies: ')
        parser.save_to_mongo_unique(result, DB_NAME, collection_name, host=HOST, port=PORT)
    else:
        choice = input('Wanna search in MongoDB(y/n)?: ').lower()
        if choice == 'y':
            parser.mongo_find(DB_NAME, collection_name='hh_vacancies', host=HOST, port=PORT)
        if choice == 'n':
            print('See ya!')
