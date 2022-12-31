from django.shortcuts import render
from utils.scraping import extract_cars_autocasion, extract_cars_coches_com, extract_cars_motor_es
from utils.whoosh_and_db import populate_db_and_create_index
from main.models import Car
from whoosh import query
from whoosh.index import open_dir
from whoosh.qparser import QueryParser, OrGroup
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

def search_by_title(request):
    if request.method == "POST":
        search = request.POST.get("search")
        cars = []
        
        if os.path.exists("Index"):
            ix = open_dir("Index")
            with ix.searcher() as searcher:

                if search == "":
                    cars = ix.searcher().documents()
                    cars = list(cars)
                    return render(request, "index.html", {"cars": cars})

                query = QueryParser("title", ix.schema, group=OrGroup).parse(search)
                cars = searcher.search(query, limit=None)
                cars = list(cars)

        return render(request, "index.html", {"cars": cars})

def search_by_specifications(request):

    #Load filters

    cars_index = []
    brands = []
    provinces = []
    fuels = []
    colors = []
    seats = []
    orders = ['Sin ordenación', 'Ascendente por km', 'Descendente por km', 'Ascendente por precio', 'Descendente por precio']

    if os.path.exists("Index"):
        ix = open_dir("Index")
        cars_index = ix.searcher().documents()
        cars_index = list(cars_index)

        for car in cars_index:

            if 'brand' in car and car['brand'] not in brands:
                brands.append(car['brand'])
            if 'province' in car and car['province'] not in provinces:
                provinces.append(car['province'])
            if 'fuel' in car and car['fuel'] not in fuels:
                fuels.append(car['fuel'])
            if 'color' in car and car['color'] not in colors:
                colors.append(car['color'])
            if 'seats' in car and car['seats'] not in seats:
                seats.append(car['seats'])

    #Load cars according to selected filters

    if request.method == "POST" and "search" in request.POST:

        brand = request.POST.get("brand")
        province = request.POST.get("province")
        fuel = request.POST.get("fuel")
        color = request.POST.get("color")
        seat = request.POST.get("seats")
        order = request.POST.get("order")

        km_min = request.POST.get("km-min")
        km_max = request.POST.get("km-max")
        price_min = request.POST.get("spot_price-min")
        spot_price_max = request.POST.get("spot_price-max")
        power_min = request.POST.get("power-min")
        power_max = request.POST.get("power-max")

        if os.path.exists("Index"):
            ix = open_dir("Index")
            with ix.searcher() as searcher:

                search = []

                if brand != "anyone":
                    search.append(query.Term("brand", brand))

                if province != "anyone":
                    search.append(query.Term("province", province))
                
                if fuel != "anyone":
                    search.append(query.Term("fuel", fuel))

                if color != "anyone":
                    search.append(query.Term("color", color))

                if seat != "anyone":
                    search.append(query.Term("seats", seat))

                range_filters = [
                    query.NumericRange("km", km_min, km_max),
                    query.NumericRange("spot_price", price_min, spot_price_max),
                    query.NumericRange("power", power_min, power_max)
                ]

                q = query.And(search + range_filters)

                if order == "Sin ordenación":
                    results = searcher.search(q, limit=None)

                else:
                    if order == "Ascendente por km":
                        results = searcher.search(q, sortedby='km', reverse=False, limit=None)
                    elif order == "Descendente por km":
                        results = searcher.search(q, sortedby='km', reverse=True, limit=None)
                    elif order == "Ascendente por precio":
                        results = searcher.search(q, sortedby='spot_price', reverse=False, limit=None)
                    else:
                        results = searcher.search(q, sortedby='spot_price', reverse=True, limit=None)

                return render(request, 'specific_cars.html', {"cars": results, 
                                                "brands": sorted(brands), 
                                                "provinces": sorted(provinces), 
                                                "fuels": sorted(fuels), 
                                                "colors": sorted(colors), 
                                                "seats": sorted(seats),
                                                "orders": orders,
                                                "selected_brand": brand,
                                                "selected_province": province,
                                                "selected_fuel": fuel,
                                                "selected_color": color,
                                                "selected_seats": int(seat),
                                                "selected_order": order,
                                                "selected_km_min": km_min,
                                                "selected_km_max": km_max,
                                                "selected_price_min": price_min,
                                                "selected_price_max": spot_price_max,
                                                "selected_power_min": power_min,
                                                "selected_power_max": power_max,
                                                })

    elif request.method == "POST" and "clean" in request.POST:

        return render(request, 'specific_cars.html', {"cars": cars_index, 
                                                "brands": sorted(brands), 
                                                "provinces": sorted(provinces), 
                                                "fuels": sorted(fuels), 
                                                "colors": sorted(colors), 
                                                "seats": sorted(seats),
                                                "orders": orders,
                                                "selected_km_min": 0,
                                                "selected_km_max": 300000,
                                                "selected_price_min": 0,
                                                "selected_price_max": 100000,
                                                "selected_power_min": 0,
                                                "selected_power_max": 500,
                                                })

    return render(request, 'specific_cars.html', {"cars": cars_index, 
                                                "brands": sorted(brands), 
                                                "provinces": sorted(provinces), 
                                                "fuels": sorted(fuels), 
                                                "colors": sorted(colors), 
                                                "seats": sorted(seats),
                                                "orders": orders,
                                                "selected_km_min": 0,
                                                "selected_km_max": 300000,
                                                "selected_price_min": 0,
                                                "selected_price_max": 100000,
                                                "selected_power_min": 0,
                                                "selected_power_max": 500,
                                                })