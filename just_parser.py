from bs4 import BeautifulSoup
import requests
from requests import get
import random
import time
import csv
import fake_useragent
import re
import json
import time
import datetime

start_time = time.time()
cities_with_metro = ["kharkov", "kiev", "dnepr"]
cities = ["kharkov", "dnepr", "odessa", "lutsk", "vinnitsa", "poltava", "ivano-frankovsk", 
            "cherkassy", "chernovtsy", "kiev", "zaporozhye", "lvov", "zhitomir", "uzhgorod",
            "rovno", "ternopol", "khmelnytskyi", "nikolaev", "kropivnitskyi"]
date = datetime.datetime.now().strftime("%Y-%m-%d")

def get_info(attribute, current_city):
    date_tm = attribute.find("time").get("datetime")

    title = attribute.find("a", class_="realty-link size22 bold break")
    title_name = title.get("title").strip()

    flat = attribute.find("div", class_="flex f-center")
    flat_price = flat.text.strip() if flat else "Ціна не знайдена"

    closer_metro = attribute.find("a", {"data-level": "metro"})
    closer_metro_name = (closer_metro.text.strip() if closer_metro else ("метро поряд відсутнє" if current_city in cities_with_metro else "у місті відсутнє метро"))

    location_area = attribute.find_all("a", {"data-level": "area"})
    location_area = (location_area[-1].text.strip() if location_area else "район не вказано")

    part_of_city = attribute.find_all("a", {"data-level": "area"})
    part_of_city = (part_of_city[0].text.strip() if part_of_city else "частина міста не вказана")

    city_name = attribute.find("span", class_="mb-5 i-block")
    city_name = (city_name.text.strip() if city_name else "інформація про місто відсутня")

    zhk_name = attribute.find("span", class_="mb-5")
    zhk_name = (zhk_name.get_text(strip=True).replace("·", "") if zhk_name else "інформація відсутня")

    rooms = attribute.find_all("span", class_="point-before")[0]
    rooms = rooms.text.strip() if rooms else "інформація відсутня"
    square = attribute.find_all("span", class_="point-before")[1]
    square = square.text.strip() if square else "інформація відсутня"
    floor = attribute.find_all("span", class_="point-before")[2]
    floor = floor.text.strip() if floor else "інформація відсутня"

    add_benefits_element = attribute.find("div", class_="labels-wrap unstyle")
    add_benefits = (add_benefits_element.get_text(strip=True) if add_benefits_element else "інформація відсутня")
    split_text = re.split(r"(?<=[а-яА-ЯіІєЄ])(?=[А-ЯІЄ])", add_benefits)

    while len(split_text) < 3:
        split_text.append("інформація відсутня")

    link = str(attribute.find("div", class_="tit").find("a").get("href"))
    full_link = "https://dom.ria.com/" + link

    flat_info_dict = {
        "Дата публікації": date_tm,
        "Ціна оренди": flat_price,
        "Вулиця & номер будинку": title_name,
        "Місто": city_name,
        "Район": location_area,
        "Частина міста": part_of_city,
        "Найближче метро": closer_metro_name,
        "Назва ЖК": zhk_name,
        "Кількість кімнат": rooms,
        "Площа": square,
        "Поверх": floor,
        "Вказані переваги_1": split_text[0],
        "Вказані переваги_2": split_text[1],
        "Вказані переваги_3": split_text[2],
        "Посилання": full_link,
    }
    return flat_info_dict


def get_flat_from_city():
    user = fake_useragent.UserAgent().random
    header = {"user-agent": user}

    data = []

    for city in cities:
        url = f"https://dom.ria.com/uk/arenda-kvartir/{city}/?page="
        resp = requests.get(url, headers=header).text
        soup = BeautifulSoup(resp, "lxml")
        try:
            number_of_pages = int(soup.find_all("a", class_="page-item button-border")[-1].text.strip())
        except Exception:
            number_of_pages = 1
            print(f"Ex/Кількість сторінок на сайті по місту {city}: {number_of_pages}")
        else:
            print(f"Кількість сторінок на сайті по місту {city}: {number_of_pages}")

        for page_num in range(1, number_of_pages + 1):
            url = f"https://dom.ria.com/uk/arenda-kvartir/{city}/?page={page_num}"
            resp = requests.get(url, headers=header).text
            soup = BeautifulSoup(resp, "lxml")
            houses_info = soup.find_all("div", class_="wrap_desc p-rel")

            for house in houses_info:  # проходимо по карточкам з інформацією
                info = get_info(house, city)
                if info in data:  # перевірка на дублікати при зборі данних, бо іноді є більше одного оголошення того самого будинка на сайті
                    continue
                else:
                    data.append(info)
            if page_num % 10 == 0:  # може бути, що сторінок буде менше ніж десять, і тоді всеж варто якось перечекати
                time.sleep(random.randint(15,20))

    with open(f"rental_info_ua_{date}.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    
    with open(f"rental_info_ua_{date}.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print("Кінцеві файли успішно створенно")


get_flat_from_city()
end_time = time.time()
print(f"Всього було витрачено {round(end_time-start_time, 2)} секунд на парсинг данних з {len(cities)} міст України")