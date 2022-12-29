import os, shutil
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, KEYWORD, NUMERIC, ID
from scraping import extract_cars_autocasion, extract_cars_coches_com, extract_cars_motor_es

def store_data_whoosh(ids, cars):
    
    schem = Schema(id = ID(),
                    title = TEXT(stored=True,phrase=False),
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
    
    for i in range(0,len(cars)):

        car = cars[i]

        writer.add_document(id = str(ids[i]),
                            title = car['title'],
                            brand = car['brand'],
                            province = car['province'],
                            spot_price = car['spot_price'],
                            km = car['km'],
                            fuel = car['fuel'],
                            power = car['power'],
                            color = car['color'],
                            seats = car['seats'])
 
    writer.commit()
    print("Fin de indexado. Se han indexado " + str(len(cars)) + " coches.")    

def create_whoosh_index(autocasion_pages = 3, coches_com_pages = 3, motor_es_pages = 3):

    autocasion_cars = extract_cars_autocasion(autocasion_pages)
    coches_com_cars = extract_cars_coches_com(coches_com_pages)
    motor_es_cars = extract_cars_motor_es(motor_es_pages)

    all_cars = autocasion_cars + coches_com_cars + motor_es_cars

    ids = [i for i in range(0,len(all_cars))]

    store_data_whoosh(ids, all_cars)