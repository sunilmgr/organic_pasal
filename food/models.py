from itertools import product
from django.conf import settings
from django.db import models
from django.utils.html import mark_safe

# Create your models here.
STATUS = (
    (0,"Draft"),
    (1,"Publish")
)

ORDER_STATUS = (
    (0,"Pending"),
    (1,"Processing"),
    (2,"Being Delivered"),
    (3,"Received"),
    (4,"Canceled")

)

class Category(models.Model):
    name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class ItemImage(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def image_tag(self):
        return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')


class Product(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=120)
    price = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    image = models.ImageField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.item.name


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



class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    Ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.CharField(max_length=200, blank=True, null=True)
    total_price = models.FloatField(blank=True, null=True, default=0)
    order_note = models.CharField(max_length=20, blank=True, null=True)
    status = models.IntegerField(choices=ORDER_STATUS, blank=True, null=True)


    def __str__(self):
        return self.user.username



class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'



class Contact(models.Model):
    name = models.CharField(max_length=130)
    email = models.CharField(max_length=130)
    phone = models.CharField(max_length=10)
    description = models.TextField()
    date = models.DateField()

    def __str__(self):
        return self.name


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField()
    description = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = "Reviews"


class Post(models.Model):
    title = models.CharField(max_length = 200, unique =True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='blog')
    metades = models.CharField(max_length=300, default="new post")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=200, unique=True)
    status = models.IntegerField(choices=STATUS, default=0)


    def __str__(self):
        return self.title

    def image_tag(self):
        return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')
