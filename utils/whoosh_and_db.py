import os, shutil
from main.models import Car, WebUser
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, KEYWORD, NUMERIC, ID, STORED
from utils.scraping import extract_cars_autocasion, extract_cars_coches_com, extract_cars_motor_es

def populate_db_and_create_index(ids, all_cars):

    for user in WebUser.objects.all():
        user.favorite_cars.clear()
        user.save()

    Car.objects.all().delete()

    aux_titles, aux_description, aux_price = [], [], []

    cars = {}

    schem = Schema(id = ID(stored=True),
                    title = TEXT(stored=True,phrase=False),
                    image = STORED(),
                    brand = ID(stored=True),
                    province = ID(stored=True),
                    spot_price = NUMERIC(stored=True, numtype=float),
                    km = NUMERIC(stored=True, numtype=int),
                    fuel = ID(stored=True),
                    power = NUMERIC(stored=True, numtype=int),
                    color = ID(stored=True),
                    seats = NUMERIC(stored=True, numtype=int))
                           
    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")
    
    ix = create_in("Index", schema=schem)
    writer = ix.writer()

    for i in range(0, len(ids)):

        car = all_cars[i]
        if insert_duplicate(car, aux_titles, aux_description, aux_price):
            continue
        
        cars[ids[i]] = Car(id = ids[i],
                        url = car['url'],
                        description = car['description'],
                        financed_price = car['financed_price'],
                        registration = car['registration'],
                        bodywork = car['bodywork'],
                        change = car['change'],
                        has_guarantee = car['guarantee'][0],
                        guarantee_time = car['guarantee'][1],
                        doors = car['doors'])

        writer.add_document(id = str(ids[i]),
                            title = car['title'],
                            image = car['img'],
                            brand = car['brand'],
                            province = car['province'],
                            spot_price = car['spot_price'],
                            km = car['km'],
                            fuel = car['fuel'],
                            power = car['power'],
                            color = car['color'],
                            seats = car['seats'])

        aux_titles.append(car['title'])
        aux_description.append(car['description'])
        aux_price.append(car['spot_price'])
    
    Car.objects.bulk_create(cars.values())
    writer.commit()

def insert_duplicate(car, aux_titles, aux_description, aux_price):

    if car['title'] in aux_titles:
        index_title = aux_titles.index(car['title'])
        if car['description'] == aux_description[index_title] and car['spot_price'] == aux_price[index_title]:
            return True
    return False