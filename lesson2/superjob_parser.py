from bs4 import BeautifulSoup as bs
import requests
import json
import time
from pandas import DataFrame


class SuperjobParser:
    def __init__(self, start_url, sleep, key_word, user_agent, retry_number=1, proxies=None):
        self.start_url = start_url
        self.retry_number = retry_number
        self.sleep = sleep
        self.params = {
            'keywords': f'{key_word}'
        }
        self.headers = {
            'User-Agent': f'{user_agent}'
        }
        self.proxies = proxies

    def _get(self, *args, **kwargs):
        for i in range(self.retry_number):
            response = requests.get(*args, **kwargs)
            if response.ok == (response.status_code < 400):
                return response
            else:
                response.raise_for_status()
                time.sleep(self.sleep)
                print('Trying again...')
                continue

    def _run(self):
        r = self._get(self.start_url, headers=self.headers, params=self.params, proxies=self.proxies)
        return r

    def check_page(self, soap):
        buttons = soap.findAll(attrs={'class': '_1BOkc'})
        buttons = [button.text for button in buttons]
        if 'Дальше' in buttons:
            return True
        else:
            return False


    def parse(self):
        vacancies = []
        is_last_page = True
        page_counter = 1
        while is_last_page:
            self.params['page'] = page_counter
            print(f'Parsing page {page_counter}...')
            response = self._run()
            soap = bs(response.text, 'html.parser')
            vacancies_info = soap.findAll(attrs={'class': 'Fo44F QiY08 LvoDO'})
            for vacancy in vacancies_info:
                vacancy_summary = {}
                vacancy_title = vacancy.find(attrs={'class': 'icMQ_'}).text
                vacancy_link = vacancy.find(attrs={'class': 'icMQ_'})['href']
                vacancy_location = vacancy.find(attrs={'class': 'clLH5'}).next_sibling.text
                vacancy_publication_date = vacancy.find(attrs={'class': '_3mfro _9fXTd _2JVkc _2VHxz'}).text
                vacancy_salary = vacancy.find(attrs={'class': '_3mfro _2Wp8I PlM3e _2JVkc _2VHxz'}).text
                is_employer_provided = vacancy.find(attrs={'class': 'f-test-text-vacancy-item-company-name'})
                if is_employer_provided:
                    vacancy_summary['employer'] = is_employer_provided.text
                else:
                    vacancy_summary['employer'] = None
                vacancy_summary['vacancy'] = vacancy_title
                vacancy_summary['link'] = 'https://superjob.ru/vacansii/' + vacancy_link
                vacancy_summary['location'] = vacancy_location
                vacancy_summary['publication_date'] = vacancy_publication_date
                if 'от' in vacancy_salary:
                    salary = vacancy_salary.split()
                    vacancy_summary['min_salary'] = ''.join(salary[1:3])
                    vacancy_summary['max_salary'] = None
                    vacancy_summary['currency'] = salary[-1]
                elif vacancy_salary == 'По договорённости':
                    vacancy_summary['min_salary'] = 'Discussable'
                    vacancy_summary['max_salary'] = 'Discussable'
                elif 'до' in vacancy_salary:
                    salary = vacancy_salary.split()
                    vacancy_summary['max_salary'] = ''.join(salary[1:3])
                    vacancy_summary['min_salary'] = None
                    vacancy_summary['currency'] = salary[-1]
                else:
                    salary = vacancy_salary.split()
                    min_salary = ''.join(salary[:2])
                    max_salary = ''.join(salary[3:5])
                    currency = salary[-1]
                    vacancy_summary['min_salary'] = min_salary
                    vacancy_summary['max_salary'] = max_salary
                    vacancy_summary['currency'] = currency
                vacancies.append(vacancy_summary)

            is_last_page = self.check_page(soap)
            page_counter += 1
        print('Parsing finished')
        print(f'Total vacancies found {len(vacancies)}' + '\n')
        return vacancies

    @staticmethod
    def save_to_json(object, path):
        with open(path, 'w') as f:
            json.dump(object, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    start_url = 'https://superjob.ru/vacancy/search/'
    proxies = {
        'http': 'http://176.241.129.113:3128'
    }
    key_word = input('Type keyword to search: ')
    path = input('Type path to save data set: ')
    retry_number = int(input('Type number of reconnects: '))
    user_agent = 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.134 Safari/537.36'
    parser = SuperjobParser(start_url, 3, key_word, user_agent=user_agent, retry_number=retry_number)
    result = parser.parse()
    choice = int(input('Type 1 to save via CSV or type 2 to save via JSON: '))
    if choice == 1:
        data_frame = DataFrame.from_records(result)
        data_frame.to_csv(path_or_buf=path, index=True)
        print(f'Saved to {path}')
    if choice == 2:
        parser.save_to_json(result, 'result.json')
        print('Saved to result.json')
