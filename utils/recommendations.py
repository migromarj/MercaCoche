import nltk
from collections import defaultdict

def recommend_cars(favorite_cars, cars_index, n=12):

    similarities = defaultdict(float)

    favorite_cars_ids = [str(car.id) for car in favorite_cars]

    for car in cars_index:
        if car['id'] not in favorite_cars_ids:
            for favorite_car in favorite_cars:

                similarities[car['id']] += calculate_similarity(car, cars_index[favorite_car.id])

    sorted_cars = sorted(similarities.items(), key=lambda x: x[1], reverse=True)

    return sorted_cars[:n]

def calculate_similarity(car1, car2):

    brand_similarity = 0.0
    price_similarity = 0.0
    province_similarity = 0.0
    km_similarity = 0.0
    fuel_similarity = 0.0
    power_similarity = 0.0
    color_similarity = 0.0
    seats_similarity = 0.0

    if aux_condition('brand', car1, car2):
        brand_similarity = calculate_text_similarity(car1['brand'], car2['brand'])
    if aux_condition('spot_price', car1, car2):
        price_similarity = calculate_price_similarity(car1['spot_price'], car2['spot_price'])
    if aux_condition('province', car1, car2):
        province_similarity = calculate_text_similarity(car1['province'], car2['province'])
    if aux_condition('km', car1, car2):
        km_similarity = calculate_km_similarity(car1['km'], car2['km'])
    if aux_condition('fuel', car1, car2):
        fuel_similarity = calculate_text_similarity(car1['fuel'], car2['fuel'])
    if aux_condition('power', car1, car2):
        power_similarity = calculate_power_similarity(car1['power'], car2['power'])
    if aux_condition('color', car1, car2):
        color_similarity = calculate_text_similarity(car1['color'], car2['color'])
    if aux_condition('seats', car1, car2):
        seats_similarity = calculate_seats_similarity(car1['seats'], car2['seats'])

    return (brand_similarity + province_similarity + price_similarity + km_similarity + fuel_similarity + power_similarity + color_similarity + seats_similarity) / 8

def aux_condition(key, car1, car2):

    if key in car1 and key in car2 and car1[key] is not None and car2[key] is not None:
        return True

    return False

def calculate_text_similarity(text1, text2):

    # Calculamos la distancia de Levenshtein entre los textos
    distance = nltk.edit_distance(text1, text2)

    return 1.0 - distance / max(len(text1), len(text2))

def calculate_price_similarity(price1, price2):

    difference = abs(price1 - price2)
    
    if difference <= 1000:
        return 0.9
        
    elif difference <= 2000:
        return 0.7
        
    elif difference <= 5000:
        return 0.5
        
    else:
        return 0.3

def calculate_km_similarity(km1, km2):

    difference = abs(km1 - km2)

    if difference <= 10000:
        return 0.9

    elif difference <= 20000:
        return 0.7

    elif difference <= 50000:
        return 0.5

    else:
        return 0.3

def calculate_power_similarity(power1, power2):

    difference = abs(power1 - power2)

    if difference <= 10:
        return 0.9

    elif difference <= 20:
        return 0.7

    elif difference <= 30:
        return 0.5

    else:
        return 0.3

def calculate_seats_similarity(seats1, seats2):

    difference = abs(seats1 - seats2)

    if difference == 0:
        return 1.0

    elif difference == 1:
        return 0.9

    elif difference == 2:
        return 0.7

    elif difference == 3:
        return 0.5

    else:
        return 0.