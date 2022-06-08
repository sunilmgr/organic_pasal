from django.conf import settings
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

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product = models.CharField(max_length=100, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    quantity = models.IntegerField(default=1)
    total_price = models.FloatField(default=0)
    note = models.CharField(max_length=200, null=True, blank=True)
    ordered_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    





    