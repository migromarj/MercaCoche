import os
from django.shortcuts import render
from whoosh import query
from whoosh.index import open_dir
from whoosh.qparser import QueryParser, OrGroup
import unidecode
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from main.forms import SearchTitleForm

INDEX_TEMPLATE = "index.html"

########## scraping.py ##########

def unidecode_values(province, fuel, color):

    if province != None:
        province = unidecode.unidecode(province).lower()
    if fuel != None:
        fuel = unidecode.unidecode(fuel).lower()
    if color != None:
        color = unidecode.unidecode(color).lower()

    return province, fuel, color

def get_brand(car_title):

    brand = car_title.split(' ')[0].upper()

    if brand == 'MERCEDES':
        brand = 'MERCEDES-BENZ'

    if brand == 'LAND':
        brand = 'LAND-ROVER'

    return brand

########## views.py ##########

# car_details(request, id), add_favorite(request, id), remove_favorite(request, id)

def load_car_details(request, id, car_db):

    car_index = None
    if os.path.exists("Index"):
        ix = open_dir("Index")
        car_index = ix.searcher().document(id=str(id))

    favorite = False
    if request.user.is_authenticated:
        user = request.user
        favorite = user.favorite_cars.filter(id=id).exists()

    return render(request, "car_details.html", {"car_db": car_db, "car_index": car_index, "favorite": favorite})

# search_by_title(request)

def search_title(request, search, title_form):

    cars = []
        
    if os.path.exists("Index"):
        ix = open_dir("Index")
        with ix.searcher() as searcher:

            if search == "":
                cars = list(ix.searcher().documents())
                elements = cars_pagination(request, cars)
                return render(request, INDEX_TEMPLATE, {"cars": elements, "title_searched": search, "title_form": title_form})

            query = QueryParser("title", ix.schema, group=OrGroup).parse(search)
            cars = list(searcher.search(query, limit=None))
            elements = cars_pagination(request, cars)
            return render(request, INDEX_TEMPLATE, {"cars": elements, "title_searched": search, "title_form": title_form})

    return render(request, INDEX_TEMPLATE, {"cars": cars, "title_searched": search, "title_form": title_form})

# search_by_specifications(request)

def load_filters():
    
    cars_index = [] 
    brands, provinces, fuels, colors, seats = [], [], [], [], []
    orders = ['Ascendente por km', 'Descendente por km', 'Ascendente por precio', 'Descendente por precio']

    if os.path.exists("Index"):
        ix = open_dir("Index")
        cars_index = list(ix.searcher().documents())

        for car in cars_index:

            brands = add_to_filter(car, brands, 'brand')
            provinces = add_to_filter(car, provinces, 'province')
            fuels = add_to_filter(car, fuels, 'fuel')
            colors = add_to_filter(car, colors, 'color')
            seats = add_to_filter(car, seats, 'seats')

        return cars_index, brands, provinces, fuels, colors, seats, orders

    return cars_index, brands, provinces, fuels, colors, seats, orders

def add_to_filter(car, filter, attribute):

    if attribute in car and car[attribute] not in filter:
        filter.append(car[attribute])
    return filter

def cars_form_values(request, form_type):

    if form_type == "POST":
        brand = request.POST.get("brand")
        province = request.POST.get("province")
        fuel = request.POST.get("fuel")
        color = request.POST.get("color")
        seat = request.POST.get("seats")
        order = request.POST.get("order")
        km_min = request.POST.get("km-min")
        km_max = request.POST.get("km-max")
        spot_price_min = request.POST.get("spot_price-min")
        spot_price_max = request.POST.get("spot_price-max")
        power_min = request.POST.get("power-min")
        power_max = request.POST.get("power-max")
    else:
        brand = request.GET.get("brand")
        province = request.GET.get("province")
        fuel = request.GET.get("fuel")
        color = request.GET.get("color")
        seat = request.GET.get("seats")
        order = request.GET.get("order")
        km_min = request.GET.get("km-min")
        km_max = request.GET.get("km-max")
        spot_price_min = request.GET.get("spot_price-min")
        spot_price_max = request.GET.get("spot_price-max")
        power_min = request.GET.get("power-min")
        power_max = request.GET.get("power-max")

        if km_min == None: km_min = 0
        if km_max == None: km_max = 300000
        if spot_price_min == None: spot_price_min = 0
        if spot_price_max == None: spot_price_max = 200000
        if power_min == None: power_min = 0
        if power_max == None: power_max = 500
    
    return brand, province, fuel, color, seat, order, km_min, km_max, spot_price_min, spot_price_max, power_min, power_max

def build_query(request, form_type):

    brand, province, fuel, color, seat, order, km_min, km_max, spot_price_min, spot_price_max, power_min, power_max = cars_form_values(request, form_type)

    search = []

    search = check_filter(search, brand, "brand")
    search = check_filter(search, province, "province")
    search = check_filter(search, fuel, "fuel")
    search = check_filter(search, color, "color")
    search = check_filter(search, seat, "seats")

    range_filters = [
        query.NumericRange("km", km_min, km_max),
        query.NumericRange("spot_price", spot_price_min, spot_price_max),
        query.NumericRange("power", power_min, power_max)
    ]

    q = query.And(search + range_filters)

    return (q, order, [brand, province, fuel, color, seat, order, km_min, km_max, spot_price_min, spot_price_max, power_min, power_max])

def check_filter(search, filter_, attribute):

    if filter_ != "anyone" and filter_ != None:
        if attribute == "seats":
            filter_ = int(filter_)
        search.append(query.Term(attribute, filter_))

    return search

def results_after_search(request, q, order, filters1, filters2):

    results = []

    if os.path.exists("Index"):
        ix = open_dir("Index")
        with ix.searcher() as searcher:

            if order == "anyone" or order == None:
                results = searcher.search(q, limit=None)

            else:
                if order == "Ascendente por km":
                    results = list(searcher.search(q, sortedby='km', reverse=False, limit=None))
                elif order == "Descendente por km":
                    results = list(searcher.search(q, sortedby='km', reverse=True, limit=None))
                elif order == "Ascendente por precio":
                    results = list(searcher.search(q, sortedby='spot_price', reverse=False, limit=None))
                else:
                    results = list(searcher.search(q, sortedby='spot_price', reverse=True, limit=None))

            results = cars_pagination(request, results)

            return sepecific_cars_view(request, results, filters1, filters2)

    return sepecific_cars_view(request, results, filters1, filters2)

def sepecific_cars_view(request, results, filters1, filters2):

    if filters2[4] != "anyone" and filters2[4] != None: filters2[4] = int(filters2[4])
    
    return render(request, 'specific_cars.html', {"cars": results,
                                                "brands": sorted(filters1[0]),
                                                "provinces": sorted(filters1[1]),
                                                "fuels": sorted(filters1[2]),
                                                "colors": sorted(filters1[3]),
                                                "seats": sorted(filters1[4]),
                                                "orders": filters1[5],
                                                "selected_brand": filters2[0],
                                                "selected_province": filters2[1],
                                                "selected_fuel": filters2[2],
                                                "selected_color": filters2[3],
                                                "selected_seats": filters2[4],
                                                "selected_order": filters2[5],
                                                "selected_km_min": filters2[6],
                                                "selected_km_max": filters2[7],
                                                "selected_price_min": filters2[8],
                                                "selected_price_max": filters2[9],
                                                "selected_power_min": filters2[10],
                                                "selected_power_max": filters2[11],
                                                })

# General para todas las funciones de listado de coches

def cars_pagination(request, cars_index):

    paginator = Paginator(cars_index, 12)
    page = request.GET.get('page')
    
    try:
        elements = paginator.page(page)
    except PageNotAnInteger:
        elements = paginator.page(1)
    except EmptyPage:
        elements = paginator.page(paginator.num_pages)

    return elements