'''
choose_category - циклическая, может быть перевызвана сколько угодно раз,
обработать останов.

'''

from parse_bags import Parser
from pprint import pprint


if __name__ == '__main__':
    p = Parser()
    url1 = p.choose_category()
    url2 = p.choose_category(url1)
    lst = p.get_item_id_from_page(url2)
    pprint(p.get_sku_id(lst))
