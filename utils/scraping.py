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


def extract_cars_autocasion(num_pages=3):
    
    url = 'https://www.autocasion.com/coches-ocasion'
    res = []
    
    options = webdriver.ChromeOptions()
    options.headless = True

    browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    for page in range(0, num_pages):

        browser.get(url + "?page=" + str(page + 1))
        time.sleep(5)
        response = browser.page_source

        soup = BeautifulSoup(response, "lxml")

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

    browser.quit()

    return res

def extract_cars_coches_com(num_pages=3):
    
    url = 'https://www.coches.com/coches-segunda-mano/coches-ocasion.htm'
    res = []
    
    for page in range(0, num_pages):

        request = urllib.request.urlopen(url + "?page=" + str(page))
        soup = BeautifulSoup(request, "lxml")

        cars_container = soup.find('div', {'class': 'pillList vo-results__card-list script__vo-results-card-list'})

        cars = cars_container.find_all('div', {'class': 'cc-car-card'})[:-1]
        
        for car in cars:
            car_url = car.find('a')['href']
            car_img = car.find('img', {'class':'cc-car-card-header-photo'})['src']

            car_info = car.find('div', {'class': 'cc-car-card-body'}).find_all('div', {'class': 'cc-car-card-body-line'})

            car_title = car_info[1].find('span').text.strip()

            prices = car_info[0].find('div', {'class': 'cc-car-card-price'})

            car_spot_price = prices.find('div', {'class': 'cc-car-card-price__cash'}).find('span', {'class':'cc-car-card-price__quantity'}).text
            
            if car_spot_price.strip() != '':
                car_spot_price = float(car_spot_price.replace('€', '').replace('.', '').strip())
            else:
                car_spot_price = None

            car_financed_price = prices.find('div', {'class': 'cc-car-card-price__financed'}).find('span', {'class':'cc-car-card-price__quantity'}).text

            if car_financed_price.strip() != '':
                car_financed_price = float(car_financed_price.replace('€', '').replace('.', '').strip())
            else:
                car_financed_price = None
            
            car_info_request = urllib.request.urlopen(car_url)
            soup_info = BeautifulSoup(car_info_request, "lxml")
            basic_data = soup_info.find('div', {'class': 'cc-car-overview cc-car-overview--r'}).find_all('div', {'class':'cc-car-overview__block'})

            car_registration = basic_data[0].find('p', {'class':'cc-car-overview__text'}).text.strip()
            car_power = basic_data[1].find('p', {'class':'cc-car-overview__text'}).text.strip()
            car_km = basic_data[2].find('p', {'class':'cc-car-overview__text'}).text.strip()
            car_fuel = basic_data[3].find('p', {'class':'cc-car-overview__text'}).text.strip()
            car_bodywork = basic_data[4].find('p', {'class':'cc-car-overview__text'}).text.strip()
            car_change = basic_data[5].find('p', {'class':'cc-car-overview__text'}).text.strip()
            car_environmental_label = basic_data[6].find('p', {'class':'cc-car-overview__text'}).text.strip()
            car_color = basic_data[7].find('p', {'class':'cc-car-overview__text'}).text.strip()
            car_guarantee = basic_data[8].find('p', {'class':'cc-car-overview__text'}).text.strip()

            car_description = soup_info.find('div', {'id': 'indexCardVehicleDescription'}).find('div', {'class':'index-card__info-text'}).find('div').text.strip()

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

def extract_cars_motor_es(num_pages=3):

    url = 'https://www.motor.es/coches-segunda-mano/'
    res = []

    for page in range(0, num_pages):

        request = urllib.request.Request(url + '?pagina=' + str(page + 1) , headers={'User-Agent': 'Mozilla/5.0'})

        webpage = urllib.request.urlopen(request).read()
        soup = BeautifulSoup(webpage, "html.parser")

        cars_container = soup.find('div', {'class': 'js-results-lists'})

        cars = cars_container.find_all('article', {'class': 'elemento-segunda-mano'})[:-1]
        
        for car in cars:
            
            car_url = car.find('a', {'class':'link boton coche-link'})['href']

            car_img = car.find('img')['src']

            car_info = car.find('span', {'class': 'datos'})

            car_title = car_info.find('h3','nombre-vehiculo').text.strip()

            prices = car_info.find('div', {'class': 'precio-section'})

            car_spot_price = prices.find('div', {'class': 'precio-contado'}).find('p', {'class':'precio'}).find('strong').text
            
            if car_spot_price.strip() != '':

                price_value = car_spot_price.replace('€', '').replace('.', '').strip()

                try:
                    car_spot_price = float(price_value)
                except:
                    car_spot_price = None

            else:
                car_spot_price = None

            car_financed_price = prices.find('div', {'class': 'precio-financiado'})

            if car_financed_price != None:

                price_value = car_financed_price.find('p', {'class':'precio'}).find('strong').text.replace('€', '').replace('.', '').strip()

                try:
                    car_financed_price = float(price_value)
                except:
                    car_financed_price = None

            request = urllib.request.Request(car_url , headers={'User-Agent': 'Mozilla/5.0'})

            webpage = urllib.request.urlopen(request).read()
            soup_info = BeautifulSoup(webpage, "html.parser")
            
            basic_data = soup_info.find('section', {'class': 'zona-contenido ficha ancho-principal'}).find_all('div')

            car_registration = basic_data[10].find('dd').text.strip()
            car_power = basic_data[7].find('dd').text.strip()
            car_km = basic_data[8].find('dd').text.strip()
            car_fuel = basic_data[6].find('dd').text.strip()
            car_bodywork = basic_data[9].find('dd').text.strip()
            car_change = basic_data[12].find('dd').text.strip()
            car_environmental_label = None
            car_color = basic_data[7].find('p')
            
            if car_color != None:
                car_color = car_color.text.strip()

            car_guarantee = basic_data[11].find('dd').text.strip()

            car_description = soup_info.find('div', {'class': 'descripcion'})

            if car_description != None:
                car_description = car_description.text.strip()

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