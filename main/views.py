import os

from main.models import Car
from main.forms import RegisterForm, LoadDataForm, RecommendationsForm

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from whoosh import query
from whoosh.index import open_dir
from whoosh.qparser import QueryParser, OrGroup

from utils.aux_functions import load_car_details, search_title, load_filters, add_to_filter, cars_form_values, build_query, check_filter, results_after_search, sepecific_cars_view, cars_pagination
from utils.recommendations import recommend_cars
from utils.scraping import extract_cars_autocasion, extract_cars_coches_com, extract_cars_motor_es
from utils.whoosh_and_db import populate_db_and_create_index

from main.forms import SearchTitleForm

# Create your views here.

INDEX_TEMPLATE = "index.html"

def index(request):

    cars = []
    title_form = SearchTitleForm()
    load_message = request.GET.get("load_message")

    if os.path.exists("Index"):
        ix = open_dir("Index")
        cars_index = list(ix.searcher().documents())

        cars = cars_pagination(request, cars_index)

    return render(request, INDEX_TEMPLATE, {"cars": cars, "title_form": title_form, "load_message": load_message})

@login_required(login_url='/login')
def load_data(request):

    if request.method == "POST":
        form = LoadDataForm(request.POST)
        if form.is_valid():

            autocasion_pages = form.cleaned_data.get("autocasion_pages")
            coches_com_pages = form.cleaned_data.get("coches_com_pages")
            motor_es_pages = form.cleaned_data.get("motor_es_pages")

            cars, n_total_cars, n_autocasion, n_coches_com, n_motor_es = extract_data(autocasion_pages, coches_com_pages, motor_es_pages)

            message = "Se han cargado e indexado " + str(n_total_cars) + " coches. De todos estos " + str(n_autocasion) + " han sido de la página de Autocasión, " + str(n_coches_com) + " de la página de coches.com y " + str(n_motor_es) + " de la página de motor.es."

            return redirect("/?load_message="+message)          

        else:
            return render(request, "load_data.html", {"form": form})

    else: 
        form = LoadDataForm()
        return render(request, "load_data.html", {"form": form})

def extract_data(autocasion_cars_pages, coches_com_cars_pages, motor_es_cars_pages):

    autocasion_cars = extract_cars_autocasion(num_pages=autocasion_cars_pages)
    coches_com_cars = extract_cars_coches_com(num_pages=coches_com_cars_pages)
    motor_es_cars = extract_cars_motor_es(num_pages=motor_es_cars_pages)

    all_cars = autocasion_cars + coches_com_cars + motor_es_cars
    ids = [i for i in range(len(all_cars))]

    populate_db_and_create_index(ids, all_cars)

    cars = []

    if os.path.exists("Index"):
        ix = open_dir("Index")
        cars = list(ix.searcher().documents())

    return (cars, len(all_cars), len(autocasion_cars), len(coches_com_cars), len(motor_es_cars))

def register(request):

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/")
    else:
        form = RegisterForm()
        
    return render(request, "registration/register.html", {"form": form})

def car_details(request, id):

    car_db = get_object_or_404(Car, id=id)
    
    return load_car_details(request, id, car_db)

@login_required(login_url='/login')
def add_favorite(request, id):
    
    car_db = get_object_or_404(Car, id=id)

    user = request.user
    user.favorite_cars.add(car_db)
    user.save()

    return redirect(to="car_details", id=id)

@login_required(login_url='/login')
def remove_favorite(request, id):

    car_db = get_object_or_404(Car, id=id)

    user = request.user
    user.favorite_cars.remove(car_db)
    user.save()

    return redirect(to="car_details", id=id)

@login_required(login_url='/login')
def favorites(request):
    
    user = request.user
    favorite_cars = user.favorite_cars.all()

    cars = []
    results = []

    if os.path.exists("Index"):
        ix = open_dir("Index")
        for car in favorite_cars:
            car_index = ix.searcher().document(id=str(car.id))
            cars.append(car_index)

        results = cars_pagination(request, cars)

    return render(request, "favorite_cars.html", {"cars": results})    

def search_by_title(request):

    if request.method == "POST":
        title_form = SearchTitleForm(request.POST)
        if title_form.is_valid():
            search = title_form.cleaned_data['title']
        else:
            search = ""

        return search_title(request, search, title_form)

    else:
        title_form = SearchTitleForm()
        title_searched = request.GET.get("title_searched")
        title_form.fields["title"].initial = title_searched

        return search_title(request, title_searched, title_form)

def search_by_specifications(request):

    cars_index, brands, provinces, fuels, colors, seats, orders = load_filters()
    filters1 = [sorted(brands), sorted(provinces), sorted(fuels), sorted(colors), sorted(seats), orders]

    if request.method == "POST" and "search" in request.POST:

        q, order, filters2 = build_query(request, "POST")
        return results_after_search(request, q, order, filters1, filters2)        

    elif request.method == "POST" and "clean" in request.POST:

        results = cars_pagination(request, cars_index)
        filters2 = [None, None, None, None, None, None, 0, 300000, 0, 200000, 0, 500]
        return sepecific_cars_view(request, results, filters1, filters2)

    else:        

        q, order, filters2 = build_query(request, "GET")
        return results_after_search(request, q, order, filters1, filters2)

@login_required(login_url='/login')
def number_recommendations(request):
    
    if request.method == "POST":
        form = RecommendationsForm(request.POST)
        if form.is_valid():
            num_cars = form.cleaned_data['num_cars']
            return redirect("/recommend_cars/" + str(num_cars))
    else:
        form = RecommendationsForm()
        
    return render(request, "number_recommendations.html", {"form": form})

@login_required(login_url='/login')
def cars_recommendation(request, n_cars):

    user = request.user
    favorite_cars = list(user.favorite_cars.all())

    cars = []
    results = []

    if os.path.exists("Index"):
        ix = open_dir("Index")
        cars_index = list(ix.searcher().documents())

        recommended_cars = recommend_cars(favorite_cars, cars_index, n_cars)

        for car in recommended_cars:
            car_to_add = ix.searcher().document(id=car[0])
            cars.append(car_to_add)

        results = cars_pagination(request, cars)


    return render(request, 'recommend_cars.html', {'cars': results, 'n_cars': n_cars})