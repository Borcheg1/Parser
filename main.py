'''
choose_category - циклическая, может быть перевызвана сколько угодно раз,
обработать останов.

'''
import os.path
from io import BytesIO
import requests
from PIL import Image
from tqdm import tqdm

from parse_bags import Parser


def main():
    parser = Parser()
    link = parser.LINK
    parent_folder = parser.folder_dir

    try:
        category_url = parser.choose_category(link)
    except Exception as e:
        print(e)
    subcategory = int(input('Продолжить выбор категории? 0 - нет, 1 - да\n'))
    while subcategory:
        try:
            category_url = parser.choose_category(link)
        except Exception as e:
            print(e)
        subcategory = int(input('Продолжить выбор категории? 0 - нет, 1 - да\n'))

    print(
        f'Ищу товары на странице №{parser.params["page"]}\n'
        f'Параметры:\nМинимальная цена = {parser.params["minPrice"]}\n'
        f'Максимальная цена = {parser.params["maxPrice"]}\n'
    )

    try:
        urls_item_id = parser.get_item_id_from_page(category_url)
    except Exception as e:
        print(e)

    print(f'Товаров найдено: {len(urls_item_id)}\n'
          f'Ищу есть ли эти товары другого цвета\n')

    try:
        urls_dict = parser.get_sku_id(urls_item_id)
    except Exception as e:
        print(e)

    counter = 0
    for value in urls_dict.values():
        counter += len(value)

    print(f'Товары всех цветов в количестве {counter} найдены.\n'
          f'Начинаю поиск изображений\n')

    for idx, tpl in enumerate(urls_dict.items()):
        folder = str(idx)
        path = os.path.join(parent_folder, folder)
        os.mkdir(path)
        json_data = {
            idx: tpl[0]
        }
        with open(f'{parent_folder}/urls.json', 'a') as file:
            file.d




    # def get_pictures_urls(self, urls_dict):
    #     picture_urls_lst = []
    #     for key, value in urls_dict.items():
    #         # key - главная ссылка на товар
    #         # value - список всех ссылок на цвета товара
    #         for url in tqdm(value):
    #             soup = self._init_driver(url)
    #             data = soup.find("picture")
    #             picture_url = str(data).split(' ')[2].split('=')[1].strip('"')
    #             picture_urls_lst.append(picture_url)
    #     return picture_urls_lst






if __name__ == '__main__':
    main()
