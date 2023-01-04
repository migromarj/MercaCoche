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
    
    Car.objects.bulk_create(cars.values())
    writer.commit()

    print("Fin de carga e indexado. Se han cargado e indexado " + str(len(cars)) + " coches.")