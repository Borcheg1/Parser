import json
import os.path
from io import BytesIO
from time import sleep
import requests
from PIL import Image
from tqdm import tqdm

from parse_bags import Parser


def main():
    parser = Parser()
    link = parser.LINK
    parent_folder = r"C:\Users\Dmitrii\Desktop\aliexpress"  # Путь до папки, куда будут сохраняться фото
    product_colors_number = 5  # Максимальное количество цветов одного товара
    max_price = 8500  # Максимальный порог диапазона цен
    max_page = 5  # Количество страниц распарсенных до изменения диапазона цен
    price_step = 401  # Изменение диапазона цен на этот шаг
    picture_size = (480, 480)
    folder_counter = 0

    if not parent_folder:
        print('Укажите путь до папки в переменной "parent_folder"')
        return

    category_url = parser.choose_category(link)
    subcategory = int(input('Продолжить выбор категории? 0 - нет, 1 - да\n'))

    while subcategory:

        category_url = parser.choose_category(category_url)
        subcategory = int(input('Продолжить выбор категории? 0 - нет, 1 - да:\n'))

    while parser.params['maxPrice'] <= max_price:
        while parser.params['page'] <= max_page:

            print(
                f'Ищу товары на странице №{parser.params["page"]}\n'
                f'Параметры:\nМинимальная цена = {parser.params["minPrice"]}\n'
                f'Максимальная цена = {parser.params["maxPrice"]}\n'
                f'...\n'
            )

            urls_item_id = parser.get_item_id_from_page(category_url)

            if urls_item_id == "END":
                print('На этой странице товары не найдены, перехожу на следующую')
                break

            print(f'\nТоваров найдено: {len(urls_item_id)}\n'
                  f'Ищу есть ли эти товары в другом цвете')
            sleep(1)
            urls_dict = parser.get_sku_id(urls_item_id, product_colors_number)

            cnt = 0
            for value in urls_dict.values():
                cnt += len(value)

            if not cnt:
                print('\nУпс, на этой странице поиск не удался, похоже капча одолела...')
                continue

            sleep(1)
            print(f'\nТовары всех цветов в количестве {cnt} найдены\n')
            sleep(1)

            for idx, tpl in enumerate(urls_dict.items()):
                key, value = tpl
                folder = str(idx + folder_counter)
                path = os.path.join(parent_folder, folder)
                if not(os.path.exists(path) and os.path.isdir(path)):
                    os.makedirs(path)
                json_data = {
                    idx + folder_counter: key.split('?')[0]
                }
                with open(f'{parent_folder}/urls.json', 'a') as file:
                    json.dump(json_data, file)

                print(f'\nНачинаю загрузку изображений товара №{idx + 1}')
                sleep(0.5)
                for number, url in enumerate(tqdm(value)):
                    duplicate = []
                    soup = parser.init_driver(url)
                    data = soup.find("picture")
                    if data:
                        picture_url = f'''http://{str(data).split(' ')[2].split('=')[1].strip('"').split('//')[1]}'''
                        if picture_url not in duplicate:
                            duplicate.append(picture_url)
                            response = requests.get(picture_url)
                            if 199 < response.status_code < 203:
                                image = Image.open(BytesIO(response.content))
                                size = picture_size
                                resize_image = image.resize(size)
                                try:
                                    resize_image.save(f'{path}/{number}.jpg')
                                except OSError:
                                    continue
            else:
                folder_counter += idx

            print(f'Изображения успешно загружены, перехожу на следующую страницу\n')
            parser.params['page'] += 1
        else:
            print('')
            parser.params['page'] = 1
            parser.params['minPrice'] += price_step
            parser.params['maxPrice'] += price_step


if __name__ == '__main__':
    main()
