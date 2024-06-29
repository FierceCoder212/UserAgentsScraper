import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def get_ua_texts(url: str) -> list[str]:
    url_response = requests.get(url)
    if url_response.status_code == 200:
        url_soup = BeautifulSoup(url_response.text, 'html.parser')
        url_ua_elements = url_soup.find_all('span', {'class': 'code'})
        return [ua_element.get_text(strip=True) for ua_element in url_ua_elements]
    return []


base_url = 'https://www.whatismybrowser.com/guides/the-latest-user-agent/'
response = requests.get(base_url)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        user_agents = soup.select('section.section-block-main-extra div.corset div.content-block-main li a')
        user_agents_links = [urljoin(base_url, user_agent.get('href')) for user_agent in user_agents]
        with ThreadPoolExecutor(max_workers=max(10, len(user_agents_links))) as executor:
            futures = [executor.submit(get_ua_texts, link) for link in user_agents_links]
            ua_data = [future.result() for future in as_completed(futures)]
        user_agent_texts = sum(ua_data, [])
        if user_agent_texts:
            with open('ua.json', 'w') as json_file:
                json_file.write(json.dumps(list(set(user_agent_texts)), indent=4))
                print('User agents successfully saved to ua.json')
    except Exception as ex:
        print(f'Exception : {ex}')
else:
    print(json.dumps({'Url': base_url, 'Status_Code': response.status_code, 'Content': response.text}))
