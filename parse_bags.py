'''
Каждые ~500 картинок менять диапазон цен
цвет, тип, материал
minPrice=4000&
maxPrice=8000
page=1
start price 500, 20 iterations, finish 8500, !+= 400!

Одна странца - 20 объектов
500

Проверка на окончание страниц
if 'Ничего не нашли' in str(soup.find('h1').text):
    print('END')

'''

import re
import json
from io import BytesIO
from pprint import pprint
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
from PIL import Image


class Parser:
    LINK = 'http://aliexpress.ru/category/202000224/luggage-bags.html'

    folder_dir = r"C:\Users\Dmitrii\Desktop\aliexpress"

    params = {
        "minPrice": 500,
        "maxPrice": 900,
        "page": 1
    }

    def __init__(self):
        pass

    @staticmethod
    def choose_category(link=LINK):
        driver = webdriver.Firefox()
        driver.get(link)
        response = driver.page_source
        driver.close()
        soup = BeautifulSoup(response, 'html.parser')
        category = {}
        for item in soup.findAll("a"):
            if 'category' in str(item.get("href")):
                list_item = str(item.get("href"))[1::].split('/')
                if len(list_item) == 3:
                    name = list_item[2].split('.')[0]
                    category[name] = '/'.join(list_item)
        choice = input(f"{list(category.keys())}\nВыбери категорию:\n")
        url = f"http://aliexpress.ru/{category[choice]}"
        return url

    def get_item_id_from_page(self, url):
        prm = self.params
        url = f"{url}?minPrice={prm['minPrice']}&maxPrice={prm['maxPrice']}&page={prm['page']}"
        driver = webdriver.Firefox()
        driver.get(url)
        response = driver.page_source
        soup = BeautifulSoup(response, 'html.parser')
        temp_set = set()
        for item in soup.findAll("a"):
            if "/item/" in str(item.get("href")):
                temp_set.add("http://aliexpress.ru" + str(item.get("href")))
        urls_item_id = list(temp_set)
        driver.close()
        return urls_item_id

    def get_sku_id(self, urls_item_id):
        dict_sku_id = {}
        for url in urls_item_id:
            driver = webdriver.Firefox()
            driver.get(url)
            response = driver.page_source
            driver.close()
            soup = BeautifulSoup(response, 'html.parser')
            data = soup.find("script", {"id": "__AER_DATA__"})
            ids = []
            lst = str(data).split('"skuId":"')[1::]
            for item in lst:
                ids.append(re.search(r"\d{4,25}", item).group(0))
            dict_sku_id[url] = ids
        urls_dict = self._prepare_sku_id(dict_sku_id)
        return urls_dict

    @staticmethod
    def _prepare_sku_id(dict_sku_ids):
        urls_dict = {}
        for idx, tpl in enumerate(dict_sku_ids.items()):
            main_url = tpl[0].split("=")[0]
            urls_dict[idx] = []
            urls_dict[idx].append(tpl[0])
            for item in tpl[1]:
                url = f"{main_url}={item}"
                if url not in urls_dict[idx]:
                    urls_dict[idx].append(url)
        return urls_dict

    @staticmethod
    def get_pictures_urls(urls_dict):
        picture_urls_lst = []
        for item in urls_dict.values():
            for url in tqdm(item):
                driver = webdriver.Firefox()
                driver.get(url)
                response = driver.page_source
                driver.close()
                soup = BeautifulSoup(response, 'html.parser')
                data = soup.find("picture")
                picture_url = str(data).split(' ')[2].split('=')[1].strip('"')
                picture_urls_lst.append(picture_url)
        return picture_urls_lst

    def next_page(self):
        self.params['page'] += 1

    def next_price(self):
        if self.params['maxPrice'] < 8500:
            self.params['minPrice'] += 400
            self.params['maxPrice'] += 400
            return True
        else:
            return False

    @staticmethod
    def _init_driver(url):
        driver = webdriver.Firefox()
        driver.get(url)
        response = driver.page_source
        driver.close()
        soup = BeautifulSoup(response, 'html.parser')
        return soup
