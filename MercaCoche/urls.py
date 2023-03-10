"""MercaCoche URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from main import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("load_data/", views.load_data, name="load_data"),
    path("", include("django.contrib.auth.urls")),
    path("register/", views.register, name="register"),
    path("car_details/<int:id>", views.car_details, name="car_details"),
    path("add_favorite/<int:id>", views.add_favorite, name="add_favorite"),
    path("remove_favorite/<int:id>", views.remove_favorite, name="remove_favorite"),
    path("favorites/", views.favorites, name="favorites"),
    path("search_title/", views.search_by_title, name="search_car_by_title"),
    path("search_by_specifications/", views.search_by_specifications, name="search_car_by_specifications"),
    path("number_recommendations/", views.number_recommendations, name="number_recommendations"),
    path("recommend_cars/<int:n_cars>", views.cars_recommendation, name="recommend_cars")
]
