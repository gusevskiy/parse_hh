import requests
from bs4 import BeautifulSoup
import fake_useragent
import urllib3
import time
import json


# Отключение предупреждений об отсутствии проверки сертификата
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_links(text):
    ua = fake_useragent.UserAgent()  # Формирование user_agent
    data = requests.get(
        url=f"https://nn.hh.ru/search/resume?area=66&isDefaultArea=true&exp_period=all_time&logic=normal&pos=full_text&fromSearchLine=true&from=employer_index_header&text={text}&page=1",
        verify=True,  # Это для отключения проверки сертификата (хз что с этой сеткой не так в офисе)
        headers={"User-Agent": ua.random},
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, "lxml")
    try:
        page_count = int(
            soup.find("div", attrs={"class": "pager"})
            .find_all("span", recursive=False)[-1]
            .find("a")
            .find("span")
            .text
        )
        print(page_count)
    except Exception as e:  # noqa: E722
        print(e)
        return

    for page in range(page_count):
        try:
            data = requests.get(
                # Нажно открыть вторую страницу сайта что бы сформировалась ссылка с вводом
                url=f"https://nn.hh.ru/search/resume?area=66&isDefaultArea=true&exp_period=all_time&logic=normal&pos=full_text&fromSearchLine=true&from=employer_index_header&text={text}&page={page}",
                verify=True,  # Это для отключения проверки сертификата (хз что с этой сеткой не так в офисе)
                headers={"User-Agent": ua.random},
            )
            if data.status_code == 200:
                print("page = ", page)
                soup = BeautifulSoup(data.content, "lxml")
                for a in soup.find_all("a", attrs={"data-qa": "serp-item__title"}):
                    # print(a)
                    yield f'https://hh.ru{a.attrs['href'].split('?')[0]}'
        except Exception as e:
            print(f"{e}")
        time.sleep(1)
    print(page_count)


def get_resume(link):
    ua = fake_useragent.UserAgent()
    data = requests.get(verify=True, url=link, headers={"user-agent": ua.random})
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, "lxml")
    # Заголовок
    try:
        title = soup.find(attrs={"class": "resume-block__title-text"}).text
    except:
        title = ""
    # Зарплата
    try:
        salary = (
            soup.find(attrs={"class": "resume-block__salary"})
            .text.replace("\u2009", " ")
            .replace("\xa0", " ")
        )
    except:
        salary = ""
    # Блок навыки
    try:
        tags = [
            tags.text
            for tags in soup.find(attrs={"class": "bloko-tag-list"}).find_all(
                attrs={"class": "bloko-tag__section_text"}
            )
        ]
    except:
        tags = []

    resume = {"title": title, "salary": salary, "tags": tags}
    return resume


if __name__ == "__main__":
    data = []
    for a in get_links('python'):
        data.append(get_resume(a))
        time.sleep(1)
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        

