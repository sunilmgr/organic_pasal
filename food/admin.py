from django.contrib import admin
from food.models import Category, Contact, Product

# Register your models here.
admin.site.register(Contact)
admin.site.register(Category)
admin.site.register(Product)