import json
import os.path
from io import BytesIO
import requests
from PIL import Image
from tqdm import tqdm

from parse_bags import Parser


def main():
    parser = Parser()
    link = parser.LINK
    parent_folder = r"C:\Users\Dmitrii\Desktop\aliexpress"  # Путь до папки, куда будут сохраняться фото
    max_price = 8500  # Максимальный порог диапазона цен
    max_page = 10  # Количество страниц распарсенных до изменения диапазона цен
    price_step = 400  # Изменение диапазона цен на этот шаг
    picture_size = (480, 480)
    folder_counter = 0

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
        subcategory = int(input('Продолжить выбор категории? 0 - нет, 1 - да:\n'))

    while parser.params['maxPrice'] <= max_price:
        while parser.params['page'] <= max_page:
            print(
                f'Ищу товары на странице №{parser.params["page"]}\n'
                f'Параметры:\nМинимальная цена = {parser.params["minPrice"]}\n'
                f'Максимальная цена = {parser.params["maxPrice"]}\n'
                f'...\n'
            )

            try:
                urls_item_id = parser.get_item_id_from_page(category_url)
            except Exception as e:
                print(e)

            if urls_item_id == "END":
                break

            print(f'Товаров найдено: {len(urls_item_id)}\n'
                  f'Ищу есть ли эти товары в другом цвете\n')

            try:
                urls_dict = parser.get_sku_id(urls_item_id)
            except Exception as e:
                print(e)

            cnt = 0
            for value in urls_dict.values():
                cnt += len(value)

            print(f'Товары всех цветов в количестве {cnt} найдены.\n'
                  f'Начинаю поиск изображений\n')

            for idx, tpl in enumerate(urls_dict.items()):
                key, value = tpl
                folder = str(idx + folder_counter)
                path = os.path.join(parent_folder, folder)
                if not(os.path.exists(path) and os.path.isdir(path)):
                    os.makedirs(path)
                json_data = {
                    idx: key.split('?')[0]
                }
                with open(f'{parent_folder}/urls.json', 'a') as file:
                    json.dump(json_data, file)

                print(f'Начинаю загрузку изображений товара №{idx + 1}\n')
                for number, url in enumerate(tqdm(value)):
                    soup = parser.init_driver(url)
                    data = soup.find("picture")
                    if data:
                        picture_url = f'''http://{str(data).split(' ')[2].split('=')[1].strip('"').split('//')[1]}'''
                        response = requests.get(picture_url)
                        if 199 < response.status_code < 203:
                            image = Image.open(BytesIO(response.content))
                            size = picture_size
                            resize_image = image.resize(size)
                            resize_image.save(f'{path}/{number}.jpg', "JPEG")

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
