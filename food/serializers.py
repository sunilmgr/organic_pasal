
from .models import *
from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('__all__')

class ItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemImage
        fields = ('__all__')

class ProductSerializer(serializers.ModelSerializer):
     class Meta:
        model = Product
        fields = ('__all__')

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ('__all__')

class OrderItemSerializer(serializers.ModelSerializer):
     class Meta:
        model = OrderItem
        fields = ('__all__')

class OrderSerializer(serializers.ModelSerializer):
     class Meta:
        model = Order
        fields = ('__all__')

class AddressSerializer(serializers.ModelSerializer):
     class Meta:
        model = Address
        fields = ('__all__')



class ContactSerializer(serializers.ModelSerializer):
     class Meta:
        model = Contact
        fields = ('__all__')


class ReviewSerializer(serializers.ModelSerializer):
     class Meta:
        model = Review
        fields = ('__all__')

class PostSerializer(serializers.ModelSerializer):
     class Meta:
        model = Post
        fields = ('__all__')



