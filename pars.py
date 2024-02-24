from bs4 import BeautifulSoup
import requests
from requests import get
import random
import time
import csv
import fake_useragent
import re
import json

def get_city():
    user = fake_useragent.UserAgent().random
    header = {"user-agent": user}

    new_colected_data = []
    cities_with_metro = ["kharkov", "kiev", "dnepr"]

    # with open("main_ds_test.json", encoding="utf-8") as file:
    #     old_data = json.load(file)
    old_data = []
    unique_sets = set()
    unique_list = []

    cities = ["kharkov", "dnepr", "odessa", "lutsk", "vinnitsa", "poltava", "ivano-frankovsk", "cherkassy", "chernovtsy", "kiev", "zaporozhye", "lvov", "zhitomir"]

    for city in cities:
        url = f"https://dom.ria.com/uk/arenda-kvartir/{city}/?page="
        resp = requests.get(url, headers=header).text
        soup = BeautifulSoup(resp, "lxml")
        number_of_pages = int(soup.find_all("a", class_="page-item button-border")[-1].text.strip())
        print(f"Кількість сторінок на сайті по місту {city}: {number_of_pages}")

        for page_num in range(1, number_of_pages + 1):
            url = f"https://dom.ria.com/uk/arenda-kvartir/{city}/?page={page_num}"
            value = random.random()
            scaled_value = 1 + (value * (9 - 5))
            time.sleep(scaled_value)
            resp = requests.get(url, headers=header).text
            soup = BeautifulSoup(resp, "lxml")
            houses_info = soup.find_all("div", class_="wrap_desc p-rel")
            houses_banner = soup.find_all("div", class_="photo- main-photo p-rel")
            break_loop = False

            for house, banner in zip(houses_info, houses_banner):  # проходимо по карточкам з інформацією
                if banner.find("div", class_="label-wrap ios-fix"):  # перевіряємо чи є помітка (якийсь запис), що квартира перевірена або в топі

                    date_tm = house.find("time").get("datetime")

                    title = house.find("a", class_="realty-link size22 bold break")
                    title_name = title.get("title")

                    flat = house.find("div", class_="flex f-center")
                    flat_price = flat.text.strip() if flat else "Ціна не знайдена"

                    closer_metro = house.find("a", {"data-level": "metro"})
                    closer_metro_name = (closer_metro.text.strip() if closer_metro else ("метро поряд відсутнє" if city in cities_with_metro else "у місті відсутнє метро"))

                    location_area = house.find_all("a", {"data-level": "area"})
                    location_area = (location_area[-1].text.strip() if location_area else "район не вказано")

                    part_of_city = house.find_all("a", {"data-level": "area"})
                    part_of_city = (part_of_city[0].text.strip() if part_of_city else "частина міста не вказана")

                    city_name = house.find("a", {"data-level": "city"})
                    city_name = (city_name.text.strip() if city_name else "інформація про місто відсутня")

                    zhk_name = house.find("span", class_="mb-5")
                    zhk_name = (zhk_name.get_text(strip=True).replace("·", "") if zhk_name else "інформація відсутня")

                    rooms = house.find_all("span", class_="point-before")[0]
                    rooms = rooms.text.strip() if rooms else "інформація відсутня"
                    square = house.find_all("span", class_="point-before")[1]
                    square = square.text.strip() if square else "інформація відсутня"
                    floor = house.find_all("span", class_="point-before")[2]
                    floor = floor.text.strip() if floor else "інформація відсутня"

                    add_benefits_element = house.find("div", class_="labels-wrap unstyle")
                    add_benefits = (add_benefits_element.get_text(strip=True) if add_benefits_element else "інформація відсутня")
                    split_text = re.split(r"(?<=[а-я])(?=[А-Я])|(?<=і)(?=З)", add_benefits)

                    while len(split_text) < 3:
                        split_text.append("інформація відсутня")

                    link = str(house.find("div", class_="tit").find("a").get("href"))
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
                
                    if flat_info_dict in old_data:
                        continue
                    else:
                        old_data.append(flat_info_dict)
                
                else:
                    date_tm = house.find("time").get("datetime")

                    title = house.find("a", class_="realty-link size22 bold break")
                    title_name = title.get("title")

                    flat = house.find("div", class_="flex f-center")
                    flat_price = flat.text.strip() if flat else "Ціна не знайдена"

                    closer_metro = house.find("a", {"data-level": "metro"})
                    closer_metro_name = (closer_metro.text.strip() if closer_metro else ("метро поряд відсутнє" if city in cities_with_metro else "у місті відсутнє метро"))

                    location_area = house.find_all("a", {"data-level": "area"})
                    location_area = (location_area[-1].text.strip() if location_area else "район не вказано")

                    part_of_city = house.find_all("a", {"data-level": "area"})
                    part_of_city = (part_of_city[0].text.strip() if part_of_city else "частина міста не вказана")

                    city_name = house.find("a", {"data-level": "city"})
                    city_name = (city_name.text.strip() if city_name else "інформація про місто відсутня")

                    zhk_name = house.find("span", class_="mb-5")
                    zhk_name = (zhk_name.get_text(strip=True).replace("·", "") if zhk_name else "інформація відсутня")

                    rooms = house.find_all("span", class_="point-before")[0]
                    rooms = rooms.text.strip() if rooms else "інформація відсутня"
                    square = house.find_all("span", class_="point-before")[1]
                    square = square.text.strip() if square else "інформація відсутня"
                    floor = house.find_all("span", class_="point-before")[2]
                    floor = floor.text.strip() if floor else "інформація відсутня"

                    add_benefits_element = house.find("div", class_="labels-wrap unstyle")
                    add_benefits = (add_benefits_element.get_text(strip=True) if add_benefits_element else "інформація відсутня")
                    split_text = re.split(r"(?<=[а-я])(?=[А-Я])|(?<=і)(?=З)", add_benefits)

                    while len(split_text) < 3:
                        split_text.append("інформація відсутня")

                    link = str(house.find("div", class_="tit").find("a").get("href"))
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

                    if flat_info_dict in old_data:  # умова перевірки нового записаного значення в старих данних
                        break_loop = True
                        break
                    else:
                        new_colected_data.append(flat_info_dict)  # наповнення окермого масива данних новими значеннями

            if break_loop:
                break

    for dictionary in new_colected_data:  # власне перевірка на дублікати в масиві нових значень
        set_representation = frozenset(dictionary.items())
        if set_representation not in unique_sets:
            unique_sets.add(set_representation)
            unique_list.append(dictionary)
    
    final_data = old_data + unique_list

    with open("main_ds_test_1.json", "w", encoding="utf-8") as file:  # запис файла формату json
        json.dump(final_data, file, indent=4, ensure_ascii=False)
    
    with open("main_dataset.csv", "w", newline="", encoding="utf-8") as csvfile:  # запис файлу в класичному форматі csv
        fieldnames = final_data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_data)

    print("Кінцеві файли успішно створенно")


get_city()

# Створення міток активних оголошень, що дозволить робити актуальний аналіз на ринку житла в містах України
# Як варіант - то можна додати інформацію з нових джерел для збільшення числа вибірки, але знову буде актуальна проблема перевірка на дублікатів
