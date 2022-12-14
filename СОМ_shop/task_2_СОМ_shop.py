"""Написать скрипт, которые соберут с сайта по всем городам адрес (город, улица,
номер дома и т.п.), координаты, время работы (разделённое по дням) и телефоны
(общий и дополнительные, если указаны)."""

import requests
from urllib import request
import json
import re
from scrapy.selector import Selector

main_response = requests.get('https://som1.ru/shops/',
                             headers = {
                                 "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
                             })  # запрос на сайт который мы хотим изучить

scripts = Selector(text = main_response.text).xpath("//script/text()").extract()
divs = Selector(text = main_response.text).xpath(
    "//div[@class='shops-address']/text()").extract()

value_list = [script.replace("cords", "latlon")
              for script in scripts if 'showShopsMap' in script]


def func(st: str):
    """Узнаем координаты на карте"""
    coords_re = re.compile(r'\((.+)\)')
    js = json.loads(coords_re.search(st).group(1).replace("'", '"'))
    return js


value_list = func(value_list[0])

for value_data in value_list:
    l = [float(cord) for cord in value_data['latlon']]
    value_data['latlon'] = l

for i, div in enumerate(divs):
    value_list[i]['address'] = div

pages = [link.split('/')[-2] for link in Selector(
    text = main_response.text).xpath("//a[@class='btn btn-blue']/@href").extract()]

for i, value_data in enumerate(value_list):
    main_response = requests.get('https://som1.ru/shops/' +
                                 pages[i] + '/', headers = {'User-Agent': 'My User Agent 1.0'})
    tbodys = Selector(text = main_response.text).xpath(
        "//table[@class='shop-info-table']/tr/td/text()").extract()
    value_data['phones'] = tbodys[-4].split(',')
    value_data['working_hours'] = [tbodys[-1]]

with open("СОМ_shop.json", "w", encoding = "utf-8") as f:  # запись в json
    json.dump(value_list, f, indent = 4, ensure_ascii = False)
