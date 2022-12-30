from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class WebUser(AbstractUser):

    id = models.AutoField(primary_key=True)
    first_name = models.CharField(verbose_name='Nombre', max_length=150)
    last_name = models.CharField(verbose_name='Apellido', max_length=150)
    email = models.EmailField(verbose_name='Email', max_length=50, unique=True)
    favorite_cars = models.ManyToManyField('Car', related_name='favorite_cars')

    def __str__(self):
        return str(self.email)
    
class Car(models.Model):

    id = models.IntegerField(primary_key=True)
    url = models.URLField(verbose_name='URL anuncio', max_length=200)
    image = models.URLField(verbose_name='URL imagen', max_length=200)
    description = models.TextField(verbose_name='Descripción', max_length=500, null=True)
    financed_price = models.DecimalField(verbose_name='Precio financiado', max_digits=10, decimal_places=2, null=True)
    registration = models.DateTimeField(verbose_name='Fecha matriculación', null=True)
    bodywork = models.CharField(verbose_name='Carrocería', max_length=50, null=True)
    change = models.CharField(verbose_name='Cambio', max_length=50, null=True)
    has_guarantee = models.BooleanField(verbose_name='Tiene garantía', default=False)
    guarantee_time = models.IntegerField(verbose_name='Tiempo de garantía', null=True)
    doors = models.SmallIntegerField(verbose_name='Número de puertas', null=True)
    
    def __str__(self):
        return str(self.id)