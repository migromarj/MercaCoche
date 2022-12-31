from bs4 import BeautifulSoup
import urllib.request
import lxml
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import datetime
from utils.aux_functions import unidecode_values

import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def extract_cars_autocasion(num_pages=3):
    
    url = 'https://www.autocasion.com/coches-ocasion'
    res = []
    
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("--log-level=3")

    browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    for page in range(0, num_pages):
       
        browser.get(url + "?page=" + str(page + 1))

        height = browser.execute_script("return document.body.scrollHeight")
        
        n_scrolls = height // 200

        scroll_position = 0

        for i in range(n_scrolls):
          
            browser.execute_script("window.scrollTo(" + str(scroll_position) + "," + str(scroll_position + 200) + ");")

            scroll_position += 200
            time.sleep(0.5)

        browser.implicitly_wait(10)

        response = browser.page_source

        soup = BeautifulSoup(response, "lxml")

        cars_container = soup.find('div', {'id': 'results-html'})
        cars = cars_container.find_all('article')
        
        for car in cars:
            car_url = url + car.find('a')['href']
            car_img = car.find('div','img-anuncio').find('img')['src']

            car_info = car.find('div', {'class': 'contenido-anuncio'})
            car_title = car_info.find('h2', {'itemprop': 'name'}).text.strip()

            car_province = car_info.find('li', {'class': 'provincia'}).text.strip()

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

            registration_date = car_registration.split('/')
            car_registration = datetime.date(int(registration_date[1]), int(registration_date[0]), 1)

            car_fuel = basic_data[1].find('span').text.strip()
            car_km = basic_data[2].find('span')
            if car_km is not None:
                car_km = int(car_km.text.replace('.','').replace("km","").strip())

            car_bodywork = basic_data[3].find('span').text.strip()
            car_change = basic_data[4].find('span').text.strip()
            try:
                car_power = int(basic_data[5].find('span').text.strip())
            except:
                car_power = None

            car_guarantee = basic_data[6].find('span').text.strip()

            if 'meses' in car_guarantee:
                car_guarantee = (True, int(car_guarantee.replace('meses', '').strip()))
            else:
                car_guarantee = (False, 0)

            car_color = basic_data[7].find('span').text.split('/')[0].split('(')[0].strip().lower()
            if car_color == '-':
                car_color = None

            blocks_data = soup_info.find('section', {'class': 'col-izq'}).find_all('div', {'class': 'bloque'})

            car_doors = None
            car_seats = None

            data_sheet = soup_info.find('div', {'class':'content-tab ficha-tecnica'})

            if data_sheet is not None and data_sheet.find('ul') is not None:
                for item in data_sheet.find('ul').find_all('li'):
                    
                    if item.find('span').text == 'Número de puertas':
                        car_doors = int(item.text.split('puertas')[1].strip())
                        
                    if item.find('span').text == 'Número de plazas':
                        car_seats = int(item.text.split('plazas')[1].strip())
                        break

            for block in blocks_data:
                
                h2 = block.find('h2')
                if h2:
                    if h2.text == 'Descripción':
                        car_description = block.find('div', {'class':'comentarios'}).text.strip()
                        break


            car_province, car_fuel, car_color = unidecode_values(car_province, car_fuel, car_color)

            res.append({
                'title': car_title,
                'brand': car_title.split(' ')[0].upper(),
                'url': car_url,
                'img': car_img,
                'province': car_province,
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
                'doors': car_doors,
                'seats': car_seats,
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

            car_province = car.find('span', {'class': 'cc-car-card-city'}).text.strip()

            if ',' in car_province:
                aux = car_province.split(',')
                car_province = aux[1].strip() + ' ' + aux[0].strip()

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
            try:
                basic_data = soup_info.find('div', {'class': 'cc-car-overview cc-car-overview--r'}).find_all('div', {'class':'cc-car-overview__block'})
            except:
                continue
            car_registration = basic_data[0].find('p', {'class':'cc-car-overview__text'}).text.strip()

            if "/" in car_registration:
                aux = car_registration.split('/')
                car_registration = datetime.date(int(aux[1]), int(aux[0]), 1)
            else:
                car_registration = datetime.date(int(car_registration), 1, 1)

            car_power = basic_data[1].find('p', {'class':'cc-car-overview__text'}).text.strip()
            
            try:
                car_power = int(car_power.split('CV')[0].strip())
            except:
                car_power = None

            car_km = basic_data[2].find('p', {'class':'cc-car-overview__text'}).text.strip()

            if car_km.strip() == 'NUEVO':
                car_km = 0
            else:
                car_km = int(car_km.split('km')[0].replace('.','').strip())

            car_fuel = basic_data[3].find('p', {'class':'cc-car-overview__text'}).text.strip()
            car_change = basic_data[5].find('p', {'class':'cc-car-overview__text'}).text.strip()
            car_color = basic_data[7].find('p', {'class':'cc-car-overview__text'}).text.split('/')[0].split('(')[0].strip().lower()
            if car_color == '-':
                car_color = None

            car_guarantee = basic_data[8].find('p', {'class':'cc-car-overview__text'}).text.strip()

            if car_guarantee.strip() == 'SÍ':
                car_guarantee = (True, None)
            else:
                car_guarantee = (False, None)

            data_sheet = soup_info.find('div', {'class': 'index-card__technical-data-section'}).find_all('div',{'class':'index-card__technical-data-item index-card__technical-data-item--all'})

            car_doors = None
            car_seats = None

            if data_sheet[4].find('div', {'class':'index-card__technical-data-info'}) != None:
                car_doors = int(data_sheet[4].find('div', {'class':'index-card__technical-data-info'}).text.strip())

            if data_sheet[5].find('div', {'class':'index-card__technical-data-info'}) != None:
                car_seats = int(data_sheet[5].find('div', {'class':'index-card__technical-data-info'}).text.strip())

            if data_sheet[9].find('div', {'class':'index-card__technical-data-info'}) != None:
                car_bodywork = data_sheet[9].find('div', {'class':'index-card__technical-data-info'}).text.strip()

            car_description = soup_info.find('div', {'id': 'indexCardVehicleDescription'}).find('div', {'class':'index-card__info-text'}).find('div').text.strip()

            car_province, car_fuel, car_color = unidecode_values(car_province, car_fuel, car_color)

            res.append({
                'title': car_title,
                'brand': car_title.split(' ')[0].upper(),
                'url': car_url,
                'img': car_img,
                'province': car_province,
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
                'doors': car_doors,
                'seats': car_seats,
                'description': car_description
            })          

    return res


def extract_cars_motor_es(num_pages=3):

    url = 'https://www.motor.es/coches-segunda-mano/'
    res = []

    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("--log-level=3")

    browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    for page in range(0, num_pages):

        request = urllib.request.Request(url + '?pagina=' + str(page + 1) , headers={'User-Agent': 'Mozilla/5.0'})

        webpage = urllib.request.urlopen(request).read()
        soup = BeautifulSoup(webpage, "html.parser")

        cars_container = soup.find('div', {'class': 'js-results-lists'})

        cars = cars_container.find_all('article', {'class': 'elemento-segunda-mano'})[:-1]
        
        for car in cars:
            
            car_url = car.find('a', {'class':'link boton coche-link'})['href']

            car_info = car.find('span', {'class': 'datos'})

            car_title = car_info.find('h3','nombre-vehiculo').text.strip()

            car_province = car_info.find('span', {'class': 'lugar'}).text.strip()

            if "(" in car_province:
                car_province = car_province.split('(')[1].split(')')[0].strip()

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

            browser.get(car_url)
            response = browser.page_source

            soup_info = BeautifulSoup(response, "html.parser")
            car_img = soup_info.find('figure',{'class':'carrusel-modelo'}).find('img')['src']
         
            basic_data = soup_info.find('section', {'class': 'zona-contenido ficha ancho-principal'}).find_all('div')

            car_registration = None
            car_power = None
            car_km = None
            car_bodywork = None
            car_fuel = None
            car_change = None
            car_color = None
            car_guarantee = (False, None)
            car_doors = None
            car_seats = None

            for data in basic_data:

                data_dd_content = data.find('dd')

                if data_dd_content != None and data_dd_content.text.strip() != '-':
                    if data.find('dt').text.strip() == 'Matriculación':
                        car_registration = data_dd_content.text.strip()
                        aux = car_registration.split('/')

                        month = aux[0]
                        try :
                            month = int(month)
                        except:
                            month = 1

                        car_registration = datetime.date(int(aux[1]), month, 1)

                    elif data.find('dt').text.strip() == 'Potencia':
                        car_power = data_dd_content.text.strip()
                        car_power = int(car_power.split(' ')[0])

                    elif data.find('dt').text.strip() == 'Kilómetros':
                        car_km = data_dd_content.text.strip()
                        car_km = int(car_km.replace('.', '').replace('Km', '').strip())

                    elif data.find('dt').text.strip() == 'Carrocería':
                        car_bodywork = data_dd_content.text.strip()

                    elif data.find('dt').text.strip() == 'Combustible':
                        car_fuel = data_dd_content.text.strip()

                    elif data.find('dt').text.strip() == 'Cambio':
                        car_change = data_dd_content.text.strip()

                    elif data.find('dt').text.strip() == 'Puertas':
                        car_doors = data_dd_content.text.strip()
                        car_doors = int(car_doors)

                    elif data.find('dt').text.strip() == 'Plazas':
                        car_seats = data_dd_content.text.strip()
                        car_seats = int(car_seats)

                    elif data.find('dt').text.strip() == 'Color exterior':
                        car_color = data_dd_content.text.split('/')[0].split('(')[0].strip().lower()

                    elif data.find('dt').text.strip() == 'Garantía':
                        car_guarantee = data_dd_content.text.strip()
                        car_guarantee = (True, int(car_guarantee.replace('meses', '').split('(')[0].strip()))

            car_description = soup_info.find('div', {'class': 'descripcion'})

            if car_description != None:
                car_description = car_description.text.strip()

            car_province, car_fuel, car_color = unidecode_values(car_province, car_fuel, car_color)

            res.append({
                'title': car_title,
                'brand': car_title.split(' ')[0].upper(),
                'url': car_url,
                'img': car_img,
                'province': car_province,
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
                'doors': car_doors,
                'seats': car_seats,
                'description': car_description
            })                    

    browser.quit()

    return res