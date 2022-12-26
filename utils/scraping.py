from bs4 import BeautifulSoup
import urllib.request
import lxml
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def extraer_coches_autocasion(num_pages=3):
    url = 'https://www.autocasion.com/coches-ocasion'
    res = []
    for page in range(0, num_pages):

        options = webdriver.ChromeOptions()
        options.headless = True

        browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        browser.get(url + "?page=" + str(page + 1))
        time.sleep(5)
        request = browser.page_source
        browser.quit()

        soup = BeautifulSoup(request, "lxml")

        cars_container = soup.find('div', {'id': 'results-html'})
        cars = cars_container.find_all('article')
        
        for car in cars:
            car_url = url + car.find('a')['href']
            car_img = car.find('div','img-anuncio').find('img')['src']

            car_info = car.find('div', {'class': 'contenido-anuncio'})
            car_title = car_info.find('h2', {'itemprop': 'name'}).text.strip()

            car_spot_price = car_info.find('p', {'class': 'precio'}).find('span').text
            car_spot_price = float(car_spot_price.replace('€', '').replace('.', '').strip())

            car_financed_price = car_info.find('p', {'class': 'precio financiado'})

            if car_financed_price:
                car_financed_price = car_financed_price.find('span').text
                car_financed_price = float(car_financed_price.replace('€', '').replace('.', '').strip())

            car_info_request = urllib.request.urlopen(car_url)
            soup_info = BeautifulSoup(car_info_request, "lxml")

            basic_data = soup_info.find('ul', {'class': 'datos-basicos-ficha'}).find_all('li')

            car_registration = basic_data[0].find('span').text.strip()
            car_fuel = basic_data[1].find('span').text.strip()
            car_km = basic_data[2].find('span')
            if car_km is not None:
                car_km = int(car_km.text.replace('.','').replace("km","").strip())

            car_bodywork = basic_data[3].find('span').text.strip()
            car_change = basic_data[4].find('span').text.strip()
            car_power = basic_data[5].find('span').text.strip()
            car_guarantee = basic_data[6].find('span').text.strip()
            car_color = basic_data[7].find('span').text.strip()
            
            car_environmental_label = None
            
            if len(basic_data) > 8:
                car_environmental_label = basic_data[8].find_all('span')[1].text.strip()

            blocks_data = soup_info.find('section', {'class': 'col-izq'}).find_all('div', {'class': 'bloque'})

            car_description = None

            for block in blocks_data:
                
                h2 = block.find('h2')
                if h2:
                    if h2.text == 'Descripción':
                        car_description = block.find('div', {'class':'comentarios'}).text.strip()
                        break

            res.append({
                'title': car_title,
                'url': car_url,
                'img': car_img,
                'spot_price': car_spot_price,
                'financed_price': car_financed_price,
                'registration': car_registration,
                'fuel': car_fuel,
                'km': car_km,
                'bodywork': car_bodywork,
                'change': car_change,
                'power': car_power,
                'guarantee': car_guarantee,
                'color': car_color,
                'environmental_label': car_environmental_label,
                'description': car_description
            })

    return res