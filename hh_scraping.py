from pprint import pprint
import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
import json


def headers_generate(browser='chrome', os='win'):
    return Headers(browser=browser, os=os).generate()

def upload_json(file_path: str, data: dict):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
def main():

    KEYWORD_SEARCH = ['django', 'flask']

    URL = 'https://spb.hh.ru'
    URL_SEARCH = f'{URL}/search/vacancy?'
    
    params = {
        'text': 'python',
        'area': ['1', '2'],
        'page': '0'
    }

    headers = headers_generate()

    html_hh_data = requests.get(
        url=URL_SEARCH,
        params=params,
        headers=headers
    )

    result = {
        'url': URL_SEARCH,
        'params': params,
        'headers': headers,
        'keyword_search': KEYWORD_SEARCH,
        'vacancies': []
    }

    soup = BeautifulSoup(html_hh_data.text, 'lxml')

    tags_a = soup.find_all('a', class_='serp-item__title')

    vacancies_links = [tag_a['href'] for tag_a in tags_a]

    for link in vacancies_links:
        html_job = requests.get(url=link, headers=headers)

        soup_job = BeautifulSoup(html_job.text, 'lxml')

        tag_div = soup_job.find('div', class_='vacancy-description')
        tags_p = tag_div.find_all('p')
        
        for tag_p in tags_p:
            if any([keyword in tag_p.text.lower() for keyword in KEYWORD_SEARCH]):
                # title
                tag_div_title = soup_job.find('div', class_='vacancy-title')
                tag_h1_title = tag_div_title.find('h1')
                title = tag_h1_title.text
                
                # salary_fork
                tags_span_salary_fork = soup_job.find('span', attrs={'data-qa': 'vacancy-salary-compensation-type-net'})
                salary_fork = tags_span_salary_fork.text.replace('\xa0', ' ')

                # required_experience
                tag_span_experience = soup_job.find('span', attrs={'data-qa': 'vacancy-experience'})
                required_experience = tag_span_experience.text

                # company
                tag_span_company = soup_job.find('span', attrs={'data-qa': 'bloko-header-2'}, class_='bloko-header-section-2 bloko-header-section-2_lite')
                company = tag_span_company.text.replace('\xa0', ' ')

                # company_hh_link
                tag_a_company_hh_link = soup_job.find('a', attrs={'data-qa': 'vacancy-company-name'}, class_='bloko-link bloko-link_kind-tertiary')
                company_hh_link = f"{URL}{tag_a_company_hh_link['href']}"

                # city
                tag_p_city = soup_job.find('p', attrs={'data-qa': 'vacancy-view-location'})
                city = tag_p_city.text

                # data
                tag_p_data = soup_job.find('p', class_='vacancy-creation-time-redesigned')
                data = tag_p_data.text.replace('\xa0', ' ')

                result['vacancies'].append({
                    'hh_link': link,
                    'title': title,
                    'salary_fork': salary_fork,
                    'required_experience': required_experience,
                    'company': company,
                    'company_hh_link': company_hh_link,
                    'city': city,
                    'data': data
                })
            
    return result


if __name__ == '__main__':
    res = main()

    pprint(res, sort_dicts=False)

    upload_json('hh_vacations.json', res)