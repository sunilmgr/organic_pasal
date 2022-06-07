from telnetlib import SE
from unittest.util import _MAX_LENGTH
from django.db import models

# Create your models here.
class Contact(models.Model):
    name = models.CharField(max_length=130)
    email = models.CharField(max_length=130)
    phone = models.CharField(max_length=10)
    description = models.TextField()
    date = models.DateField()

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Product(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=120)
    price = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    image = models.ImageField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


    