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
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver


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

    # Выбираем категорию, может быть перевызвана сколько угодно раз

    def choose_category(self, link=LINK):
        """
        Парсим url'ы подкатегорий и сплитим из них названия.

        :param link: - url на любую категорию товаров -> str
        :return: url на выбранную подкатегорию -> str
        """
        soup = self._init_driver(link)
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
        """
        Добавляем к url'у параметры и парсим url'ы всех товаров со страницы,
        попутно избавляясь от дубликатов.

        :param url: url на категорию товаров -> str
        :return: список url'ов на товары -> list
        """
        prm = self.params
        url = f"{url}?minPrice={prm['minPrice']}&maxPrice={prm['maxPrice']}&page={prm['page']}"
        soup = self._init_driver(url)
        temp_set = set()
        for item in soup.findAll("a"):
            if "/item/" in str(item.get("href")):
                temp_set.add("http://aliexpress.ru" + str(item.get("href")))
        urls_item_id = list(temp_set)
        return urls_item_id

    def get_sku_id(self, urls_item_id):
        """
        Парсим параметр sku_id для каждого товара, склеиваем url товара с параметром sku_id и
        кладем список всех url'ов одного товара под один ключ.
        Параметр sku_id ведет на страницу с этим товаром другого цвета.

        :param urls_item_id: список url'ов на товары -> list
        :return: словарь, где
            key: произвольный номер товара в диапазоне 0-19;
            value: список url'ов на все цвета товара. -> dict
        """
        dict_sku_id = {}
        for url in urls_item_id:
            soup = self._init_driver(url)
            data = soup.find("script", {"id": "__AER_DATA__"})
            ids = []
            lst = str(data).split('"skuId":"')[1::]
            for item in lst:
                ids.append(re.search(r"\d{4,25}", item).group(0))  # поиск sku_id (первое вхождение диапазона цифр 4-25)
            dict_sku_id[url] = ids
        urls_dict = self._prepare_sku_id(dict_sku_id)
        return urls_dict

    def get_pictures_urls(self, urls_dict):
        picture_urls_lst = []
        for item in urls_dict.values():
            for url in tqdm(item):
                soup = self._init_driver(url)
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
    def _prepare_sku_id(dict_sku_ids):
        """
        Преобразовываем словарь вида:
            key: url на товар
            value: sku_id
        в словарь:
            key: произвольный номер от 0-19
            value: список готовых url'ов на цвета товара (url на товар + sku_id)

        :param dict_sku_ids: -> dict
        :return: -> dict
        """
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
    def _init_driver(url):
        """
        Инициализируем driver, вытаскиваем из url'а данные,
        инициализируем BeautifulSoup

        :param url: url на страницу, из которой хотим достать данные -> str
        :return: объект класса BeautifulSoup, в котором находится html код страницы -> bs4.BeautifulSoup
        """
        driver = webdriver.Firefox()
        driver.get(url)
        response = driver.page_source
        driver.close()
        soup = BeautifulSoup(response, 'html.parser')
        return soup
