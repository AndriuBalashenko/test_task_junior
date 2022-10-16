from geopy.geocoders import Nominatim
from bs4 import BeautifulSoup
import requests
import json


user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
             "Chrome/102.0.5005.63 Safari/537.36"
headers = {'User-Agent': user_agent}
geolocator = Nominatim(user_agent= user_agent)

url = "https://oriencoop.cl/sucursales.htm"
page = requests.get(url)
date =  BeautifulSoup(page.text, "html.parser")
links = [
    a.get('href') for a in date.find_all('a')
    if a.get('href') and a.get('href').startswith('/sucursales/')] # получаем ссылки на города


results = [] # список, который мы занесем в json

def pages(x:str):
    """Данная функция проходит все города из списка полученного с сайта и получает ответ"""

    return requests.get ( 'https://oriencoop.cl/' + x).text


def result(pages:str) -> list:
    """Данная функция получает дынные из функции pages и получает ответ в виде списка"""

    date = BeautifulSoup(pages, "html.parser")
    dat = date.find_all("div", {'class': 's-dato'})
    for date in dat:
        adres = date.find_all(['span', '\n'])
        location = geolocator.geocode(adres[0].text) # получение геоданных через адрес
        results.append({
            "address": adres[0].text,
            "latlon": [location.latitude, location.longitude],
            "name": "Oriencoop",
            "phones": [adres[1].text],
            "working_hours": [adres[3].text.strip(), adres[4].text.strip()]
        })
    return results

for i in links:
    result(pages(i))

with open("task_1.json", "a", encoding = "utf-8") as f:
        json.dump(results, f, indent = 4, ensure_ascii = False)