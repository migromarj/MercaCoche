from django.shortcuts import render
from utils.scraping import extract_cars_autocasion, extract_cars_coches_com, extract_cars_motor_es
from utils.whoosh_and_db import populate_db_and_create_index
from main.models import Car
from whoosh.index import open_dir
import os
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from main.forms import RegisterForm
from django.contrib import messages

# Create your views here.

def index(request):

    cars_index = []

    if os.path.exists("Index"):
        ix = open_dir("Index")
        cars_index = ix.searcher().documents()
        cars_index = list(cars_index)

    return render(request, 'index.html', {"cars": cars_index})

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

    cars_db = Car.objects.all() 

    cars_index = []

    if os.path.exists("Index"):
        ix = open_dir("Index")
        cars_index = ix.searcher().documents()
        cars_index = list(cars_index)

    return render(request, 'index.html', {"cars": cars_index})

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/")
    else:
        form = RegisterForm()
        
    errors = form.errors
    errors = errors.as_data()
    errors = {k: v[0].message for k, v in errors.items()}

    if 'first_name' in errors:
        errors['Nombre'] = errors['first_name']
        del errors['first_name']
    if 'last_name' in errors:
        errors['Apellido'] = errors['last_name']
        del errors['last_name']
    if 'username' in errors:
        errors['Nombre de usuario'] = errors['username']
        del errors['username']
    if 'email' in errors:
        errors['Email'] = errors['email']
        del errors['email']
        if errors['Email'] == 'Ya existe %(model_name)s con este %(field_label)s.':
            errors['Email'] = 'Ya existe un usuario con este email.'
    if 'password1' in errors:
        errors['Contraseña'] = errors['password1']
        del errors['password1']
    if 'password2' in errors:
        errors['Confirmar contraseña'] = errors['password2']
        del errors['password2']

    return render(request, "registration/register.html", {"form": form, "messages": errors})

def car_details(request, id):
    car_db = Car.objects.get(id=id)
    car_index = None
    if os.path.exists("Index"):
        ix = open_dir("Index")
        car_index = ix.searcher().document(id=str(id))

    favorite = False
    if request.user.is_authenticated:
        user = request.user
        favorite = user.favorite_cars.filter(id=id).exists()

    return render(request, "car_details.html", {"car_db": car_db, "car_index": car_index, "favorite": favorite})

def add_favorite(request, id):
    
    car_db = Car.objects.get(id=id)
    user = request.user
    user.favorite_cars.add(car_db)
    user.save()

    car_index = None
    if os.path.exists("Index"):
        ix = open_dir("Index")
        car_index = ix.searcher().document(id=str(id))

    favorite = False
    if request.user.is_authenticated:
        user = request.user
        favorite = user.favorite_cars.filter(id=id).exists()

    return render(request, "car_details.html", {"car_db": car_db, "car_index": car_index, "favorite": favorite})

def remove_favorite(request, id):

    car_db = Car.objects.get(id=id)
    user = request.user
    user.favorite_cars.remove(car_db)
    user.save()

    car_index = None
    if os.path.exists("Index"):
        ix = open_dir("Index")
        car_index = ix.searcher().document(id=str(id))

    favorite = False
    if request.user.is_authenticated:
        user = request.user
        favorite = user.favorite_cars.filter(id=id).exists()

    return render(request, "car_details.html", {"car_db": car_db, "car_index": car_index, "favorite": favorite})

def favorites(request):
    
    user = request.user
    favorites_cars = user.favorite_cars.all()

    cars = []

    if os.path.exists("Index"):
        ix = open_dir("Index")
        for car in favorites_cars:
            car_index = ix.searcher().document(id=str(car.id))
            cars.append(car_index)

    return render(request, "favorite_cars.html", {"cars": cars})