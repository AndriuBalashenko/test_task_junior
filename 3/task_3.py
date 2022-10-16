"""Написать скрипт, которые соберут с сайта по всем городам адрес (город, улица,
номер дома и т.п.), координаты, время работы (разделённое по дням) и телефоны
(общий и дополнительные, если указаны)."""

import requests
import json
import re
from scrapy.selector import Selector

main_response = requests.get('https://naturasiberica.ru/our-shops/', headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/51.0.2704.103 Safari/537.36"
})  # запрос на сайт который мы хотим изучить

items = Selector(text = main_response.text).xpath('//p[@class="card-list__description"]/text()').extract()

pages = [item.split('/')[-2] for item in Selector(text = main_response.text).xpath('//a[@class="card-list__link"]/'
                                                                                   '@href').extract()]

headline = Selector(text = main_response.text).xpath('//*[@id="bx_1573527503_444"]/div[2]/h2/text()').get().split(' ')
name = headline[-2] + ' ' + headline[-1]

adress = []

value_list = []

for item in items:
    adress.append(item.replace('\t', '').replace('\r\n', ''))

for i, page in enumerate(pages):
    data = dict()  # словарь будущий json
    data['address'] = adress[i]

    main_response = requests.get(f'https://www.google.com/maps/search/{adress[i]}')  # запрос для извлечения координат

    data['latlon'] = [float(coord) for coord in
                      re.split('&|=|%2C', Selector(text = main_response.text).xpath('//meta[''@itemprop="image"]/@content').get())[1:3]]


    res = requests.get('https://naturasiberica.ru/our-shops/' + page)  # #запрос по всем страницам из переменной page

    data['name'] = name
    data['phones'] = Selector(text = res.text).xpath('//*[@id="shop-phone-by-city"]/text()').extract()
    data['working_hours'] = Selector(text = res.text).xpath('//*[@id="schedule1"]/text()').extract()
    print(f'Collecting data from {page}... ' + f'{i + 1} of {len(pages)}')
    value_list.append(data)

with open("task_3.json", "w", encoding = "utf-8") as f:  # запись в json
    json.dump(value_list, f, indent = 4, ensure_ascii = False)
