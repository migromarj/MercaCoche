from django.shortcuts import render
from utils.scraping import extract_cars_autocasion, extract_cars_coches_com, extract_cars_motor_es
from utils.whoosh_and_db import populate_db_and_create_index

# Create your views here.

def index(request):
    return render(request, 'index.html')

def load_data(request):

    autocasion_pages = 3
    coches_com_pages = 3
    motor_es_pages = 3

    autocasion_cars = extract_cars_autocasion(autocasion_pages)
    coches_com_cars = extract_cars_coches_com(coches_com_pages)
    motor_es_cars = extract_cars_motor_es(motor_es_pages)

    all_cars = autocasion_cars + coches_com_cars + motor_es_cars

    ids = [i for i in range(0,len(all_cars))]

    populate_db_and_create_index(ids, all_cars)

    return render(request, 'index.html')