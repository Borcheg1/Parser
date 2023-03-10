import re
from time import sleep

from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium.webdriver import Firefox, FirefoxOptions


class Parser:
    LINK = 'http://aliexpress.ru/category/202000224/luggage-bags.html'

    params = {
        "minPrice": 500,
        "maxPrice": 900,
        "page": 1
    }

    def choose_category(self, link=LINK):
        """
        Парсим url'ы подкатегорий и сплитим из них названия.

        :param link: - url на любую категорию товаров -> str
        :return: url на выбранную подкатегорию -> str
        """
        soup = self.init_driver(link)
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
        :return: "END" если на странице нет товаров -> str
        :return: список url'ов на товары -> list
        """
        prm = self.params
        url = f"{url}?minPrice={prm['minPrice']}&maxPrice={prm['maxPrice']}&page={prm['page']}"
        soup = self.init_driver(url)
        if 'Ничего не нашли' in str(soup.find('h1').text):
            return "END"
        temp_set = set()
        for item in soup.findAll("a"):
            if "/item/" in str(item.get("href")):
                temp_set.add("http://aliexpress.ru" + str(item.get("href")))
        urls_item_id = list(temp_set)
        return urls_item_id

    def get_sku_id(self, urls_item_id, product_colors_number):
        """
        Парсим параметр sku_id для каждого товара, склеиваем url товара с параметром sku_id и
        кладем список всех url'ов одного товара под один ключ.
        Параметр sku_id ведет на страницу с этим товаром другого цвета.

        :param urls_item_id: список url'ов на товары -> list
        :param product_colors_number: максимальное для поиска количество товаров в другом цвете -> int
        :return: словарь, где
            key: url на товар;
            value: список url'ов на все цвета этого товара. -> dict
        """
        dict_sku_id = {}
        for url in tqdm(urls_item_id):
            soup = self.init_driver(url)
            data = soup.find("script", {"id": "__AER_DATA__"})
            ids = []
            lst = str(data).split('"skuId":"')[1::]
            for idx, item in enumerate(lst):
                if idx < product_colors_number:  # -1 потому что _prepare_sku_id добавляет
                    ids.append(re.search(r"\d{4,25}", item).group(0))  # поиск sku_id (первое вхождение диапазона цифр 4-25)
            dict_sku_id[url] = ids
        urls_dict = self._prepare_sku_id(dict_sku_id)
        return urls_dict

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
            key: url на товар с параметром sku_id
            value: sku_id
        в словарь:
            key: url на товар
            value: список готовых url'ов на цвета товара (url на товар + sku_id)

        :param dict_sku_ids: -> dict
        :return: -> dict
        """
        urls_dict = {}
        for key, value in dict_sku_ids.items():
            main_url = key.split("=")[0]
            urls_dict[main_url] = []
            # urls_dict[main_url].append(key)
            for item in value:
                if "?sku_id" in main_url:
                    url = f"{main_url}={item}"
                else:
                    url = f"{main_url}?sku_id={item}"
                if url not in urls_dict[main_url]:
                    urls_dict[main_url].append(url)
        return urls_dict

    @staticmethod
    def init_driver(url):
        """
        Инициализируем driver; вытаскиваем из url'а данные;
        инициализируем BeautifulSoup; если вылезает капча, ждем и пробуем снова этот же url

        :param url: url на страницу, из которой хотим достать данные -> str
        :return: объект класса BeautifulSoup, в котором находится html код страницы -> bs4.BeautifulSoup
        """
        options = FirefoxOptions()
        options.add_argument("--height==300")
        options.add_argument("--weight==300")
        driver = Firefox(options=options)
        driver.get(url)
        response = driver.page_source
        driver.close()
        soup = BeautifulSoup(response, 'html.parser')
        while (
                soup.find('div', {"class": "warning-text"}) is not None or
                soup.find('div', {"class": "warnning-text"}) is not None
        ):
            options = FirefoxOptions()
            options.add_argument("--height==300")
            options.add_argument("--weight==300")
            driver = Firefox(options=options)
            driver.get(url)
            response = driver.page_source
            driver.close()
            soup = BeautifulSoup(response, 'html.parser')
            sleep(300)
        return soup
