"""Написать скрипт, которые соберут с сайта по всем городам адрес (город, улица,
номер дома и т.п.), координаты, время работы (разделённое по дням) и телефоны
(общий и дополнительные, если указаны)."""

import requests
import json
import re
from scrapy.selector import Selector


def local_map(map_url: str) -> list:
    """Узнаем координаты на карте"""
    coords_re = re.compile(r'\!2d([^!]+)\!3d([^!]+)')
    return list(map(float, coords_re.search(map_url).group(1, 2)))


def working_time(span_list) -> list:
    """Режим работы учреждения"""
    morning_time_list = span_list[0].replace('.', ':').split(' ')
    evening_time_list = span_list[1].replace('.', ':').split(' ')
    mon_thu_time = 'mon-thu ' + morning_time_list[2] + '-' + morning_time_list[4] + ' ' \
                   + evening_time_list[2] + '-' + evening_time_list[4]
    fri_time = 'fri ' + morning_time_list[2] + '-' + morning_time_list[4] + ' ' \
               + evening_time_list[2] + '-' + evening_time_list[-3]
    return [mon_thu_time, fri_time]


main_response = requests.get('https://oriencoop.cl/sucursales.htm', headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
})  # запрос на сайт который мы хотим изучить
value_list = []

pages = [st.split('/')[-1] for st in Selector(
    text = main_response.text).xpath("//ul[@class='sub-menu']/li/a/@href").extract()]  # достаем все допустимые ссылки

for page in pages:
    response = requests.get('https://oriencoop.cl/sucursales/' + page)
    print('Collecting data from ' + page + 'page...')

    div = Selector(text = response.text).xpath(
        "//div[@class='s-dato']/p").extract()
    mapa_url = Selector(text = response.text).xpath(
        "//div[@class='s-mapa']/iframe/@src").get()

    data = dict()  # словарь будущий json

    time_span_list = Selector(text = div[3]).xpath("//span/text()").extract()

    data['address'] = Selector(text = div[0]).xpath("//span/text()").get()
    data['latlon'] = local_map(mapa_url)
    data['name'] = Selector(text = response.text).xpath(
        '//div[@class="s-dato"]/h3/text()').get()
    data['phones'] = [
        Selector(text = div[1]).xpath("//span/text()").get(),
        *Selector(text = response.text).xpath("//li[@class='call']/a/text()").extract()
    ]
    data['working_hours'] = working_time(time_span_list)
    value_list.append(data)

with open("Oriencoop.json", "a", encoding = "utf-8") as f:  # запись в json
    json.dump(value_list, f, indent = 4, ensure_ascii = False)
