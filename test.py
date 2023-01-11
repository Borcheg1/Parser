import re
import urllib
from pprint import pprint
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from PIL import Image


dct = {'http://aliexpress.ru/item/1005003279108272.html?sku_id=12000024995908119': ['12000024995908118',
                                                                              '12000024995908116',
                                                                              '12000024995908120',
                                                                              '12000024995908121'],
 'http://aliexpress.ru/item/1005003428466124.html?sku_id=12000025739937548': ['12000025739937547',
                                                                              '12000025739937546',
                                                                              '12000025739937548',
                                                                              '12000026337277604',
                                                                              '12000026337277603',
                                                                              '12000026337277602',
                                                                              '12000026337277601',
                                                                              '12000026337277600',
                                                                              '12000026337277599',
                                                                              '12000026337277598',
                                                                              '12000026337277597',
                                                                              '12000026337277596',
                                                                              '12000026337277595',
                                                                              '12000026337277594',
                                                                              '12000026337277593',
                                                                              '12000026337277592',
                                                                              '12000026337277591',
                                                                              '12000026337277590',
                                                                              '12000026337277589',
                                                                              '12000026337277588',
                                                                              '12000026337277587',
                                                                              '12000026337277586',
                                                                              '12000026337277585',
                                                                              '12000026337277584',
                                                                              '12000026337277583',
                                                                              '12000026337277582',
                                                                              '12000026337277581',
                                                                              '12000026337277580',
                                                                              '12000026337277579',
                                                                              '12000026337277578'],
 'http://aliexpress.ru/item/1005003835632000.html?sku_id=12000027304498874': ['12000027304498874'],
 'http://aliexpress.ru/item/1005004285200595.html?sku_id=12000028628124944': [],
 'http://aliexpress.ru/item/1005004634752105.html?sku_id=12000029917599418': ['12000029917599412',
                                                                              '12000029917599413',
                                                                              '12000029917599414',
                                                                              '12000029917599415',
                                                                              '12000029917599409',
                                                                              '12000029917599410',
                                                                              '12000029917599411',
                                                                              '12000029917599416',
                                                                              '12000029917599417',
                                                                              '12000029917599418'],
 'http://aliexpress.ru/item/1005004651868071.html?sku_id=12000029984339817': [],
 'http://aliexpress.ru/item/1005004652014755.html?sku_id=12000029985843274': ['12000029985843271',
                                                                              '12000029985843281',
                                                                              '12000029985843280',
                                                                              '12000029985843282',
                                                                              '12000029985843277',
                                                                              '12000029985843276',
                                                                              '12000029985843279',
                                                                              '12000029985843278',
                                                                              '12000029985843273',
                                                                              '12000029985843272',
                                                                              '12000029985843275',
                                                                              '12000029985843274'],
 'http://aliexpress.ru/item/1005004652138780.html?sku_id=12000029986415462': ['12000029986415462',
                                                                              '12000029986415460',
                                                                              '12000029986415461',
                                                                              '12000029986415458',
                                                                              '12000029986415459',
                                                                              '12000029986415456',
                                                                              '12000029986415457'],
 'http://aliexpress.ru/item/1005004717623919.html?sku_id=12000030509397066': ['12000030661926537',
                                                                              '12000030842297690',
                                                                              '12000030842297691',
                                                                              '12000030661926539',
                                                                              '12000030509397073',
                                                                              '12000030661926538',
                                                                              '12000030718873041',
                                                                              '12000030509397066',
                                                                              '12000030509397067',
                                                                              '12000030509397070',
                                                                              '12000030509397068',
                                                                              '12000030509397069'],
 'http://aliexpress.ru/item/1005004816240804.html?sku_id=12000030598096223': ['12000030598096222',
                                                                              '12000030598096225'],
 'http://aliexpress.ru/item/1005004818214538.html?sku_id=12000030604443893': ['12000030604443892',
                                                                              '12000030604443894',
                                                                              '12000030604443895'],
 'http://aliexpress.ru/item/1005004821290103.html?sku_id=12000030614657341': [],
 'http://aliexpress.ru/item/1005004856376423.html?sku_id=12000030765571167': ['12000030765571167',
                                                                              '12000030765571166',
                                                                              '12000030765571165'],
 'http://aliexpress.ru/item/1005004856442019.html?sku_id=12000030765440410': ['12000030765440409',
                                                                              '12000030765440408',
                                                                              '12000030765440410',
                                                                              '12000030765440405',
                                                                              '12000030765440404',
                                                                              '12000030765440407',
                                                                              '12000030765440406',
                                                                              '12000030765440400',
                                                                              '12000030765440403',
                                                                              '12000030765440402'],
 'http://aliexpress.ru/item/1005004856445038.html?sku_id=12000030765365723': ['12000030765365724',
                                                                              '12000030765365726',
                                                                              '12000030765365727',
                                                                              '12000030765365722',
                                                                              '12000030765365723'],
 'http://aliexpress.ru/item/1005004868192627.html?sku_id=12000030818669814': [],
 'http://aliexpress.ru/item/1005004872542541.html?sku_id=12000030837468864': ['12000030837468863'],
 'http://aliexpress.ru/item/1005004894659458.html?sku_id=12000030926112698': [],
 'http://aliexpress.ru/item/1005004963560607.html?sku_id=12000031173473932': ['12000031173473919',
                                                                              '12000031173473918',
                                                                              '12000031173473917',
                                                                              '12000031173473916',
                                                                              '12000031173473915',
                                                                              '12000031173473914',
                                                                              '12000031173473913',
                                                                              '12000031173473912',
                                                                              '12000031173473911',
                                                                              '12000031173473910',
                                                                              '12000031173473909',
                                                                              '12000031173473908',
                                                                              '12000031173473907',
                                                                              '12000031173473906',
                                                                              '12000031173473905',
                                                                              '12000031173473904',
                                                                              '12000031173473903',
                                                                              '12000031173473902',
                                                                              '12000031173473901',
                                                                              '12000031173473900',
                                                                              '12000031173473899',
                                                                              '12000031173473898',
                                                                              '12000031173473897',
                                                                              '12000031173473896',
                                                                              '12000031173473895',
                                                                              '12000031173473894',
                                                                              '12000031173473893',
                                                                              '12000031173473892',
                                                                              '12000031173473891',
                                                                              '12000031173473932',
                                                                              '12000031173473931',
                                                                              '12000031173473930',
                                                                              '12000031173473929',
                                                                              '12000031173473928',
                                                                              '12000031173473927',
                                                                              '12000031173473926',
                                                                              '12000031173473925',
                                                                              '12000031173473924',
                                                                              '12000031173473923',
                                                                              '12000031173473922',
                                                                              '12000031173473921',
                                                                              '12000031173473920'],
 'http://aliexpress.ru/item/1005005009621077.html?sku_id=12000031467789452': ['12000031331443623',
                                                                              '12000031467789451',
                                                                              '12000031467789450',
                                                                              '12000031467789452']}
cnt = 0
for value in dct.values():
    cnt += len(value)
print(cnt)

# url = 'https://aliexpress.ru/item/32688006671.html'

# urls_dict = {
#     0: ['http://aliexpress.ru/item/1005004309845677.html?sku_id=12000028706318934'],
#     1: ['http://aliexpress.ru/item/1005003940554748.html?sku_id=12000027520136823',
#         'http://aliexpress.ru/item/1005003940554748.html?sku_id=12000027520136815']
# }
# lst = []

url = 'https://ae04.alicdn.com/kf/S3c54e50c034a47dbb1be7fc973f57aaeo.jpg_640x640.jpg'

# driver = webdriver.Firefox()
# driver.get(url)
# response = driver.page_source
# driver.close()
# soup = BeautifulSoup(response, 'html.parser')
# print(type(url))

# for item in urls_dict.values():
#     for url in tqdm(item):
#         driver = webdriver.Firefox()
#         driver.get(url)
#         response = driver.page_source
#         driver.close()
#         soup = BeautifulSoup(response, 'html.parser')
#         data = soup.findAll("span")
#         lst.append(data)
# pprint(lst)

# nice = re.search(r"\d{4,25}", lst)
# print(nice.group(0))

# driver = webdriver.Firefox()
# driver.get(url)
# response = driver.page_source
# soup = BeautifulSoup(response, 'html.parser')
# data = soup.find("script", {"id": "__AER_DATA__"})
# ids = []
# lst = str(data).split('"skuId":"')[1::]
# for item in lst:
#     ids.append(re.search(r"\d{4,25}", item).group(0))
# pprint(ids)

# def prepare_sku_id(dict_sku_ids):
#     for key, item in dict_sku_ids.items():
#         firs_sku_id = key.split('=')[1]
#         dict_sku_ids[key].append(firs_sku_id)
#         dict_sku_ids[key] = list(set(dict_sku_ids[key]))
#
#     return dict_sku_ids

# def prepare_sku_id(dict_sku_ids):
#     urls_dict = {}
#     for idx, tpl in enumerate(dict_sku_ids.items()):
#         main_url = tpl[0].split("=")[0]
#         urls_dict[idx] = []
#         urls_dict[idx].append(tpl[0])
#         for item in tpl[1]:
#             url = f"{main_url}={item}"
#             if url not in urls_dict[idx]:
#                 urls_dict[idx].append(url)
#     return urls_dict




# prepare_sku_id(dct)

#
#
# LINK = 'https://aliexpress.ru/item/4000061482171.html'
#
# driver = webdriver.Firefox()
# driver.get(LINK)
# response = driver.page_source
# # driver.close()
# soup = BeautifulSoup(response, 'html.parser')
# #
#
# data = soup.find("script", {"id": "__AER_DATA__"})
# ids = []
# lst = str(data).split('"skuId":"')[1::]
# for item in lst:
#     ids.append(item[:17])
# pprint(ids)

# response = requests.get(LINK).content
#
# soup = BeautifulSoup(response, 'html.parser')
#
# if 'Ничего не нашли' in str(soup.find('h1').text):
#     print('END')


# LINK = 'https://aliexpress.ru/item/4000061482171.html'
#
# response = requests.get(LINK).text
# pprint(response)
# soup = BeautifulSoup(response, 'html.parser')
#
# lst = []
# for item in soup.findAll("picture"):
#     lst.append(item)
#
# pprint(lst)


