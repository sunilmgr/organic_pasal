from food.serializers import *
from rest_framework.views import APIView
from food.models import *
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from .serializers import *
from .models import *
from django.http import JsonResponse
from organic_pasal.settings import EMAIL_HOST_USER
import json
from django.core.mail import send_mail, BadHeaderError
from django.core import serializers
from time import time
from django.db.models import Max, Min
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions

# Create your views here.

def create_ref_code():
    return str(int(time()))


class CheckoutView(APIView):
    def post(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            total_price = float(order.get_total())
            if total_price > 0:
                address = self.request.data['address']
                try:
                    save_order_db(order, total_price, address)
                except Exception as e:
                    return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

                
                products = []
                for item in order.items.all():
                    products.append(item)
                my_items = ''.join(str(v) + ',\n' for v in products)
                subject = "Order Confirmation - Organic Pasal"
                message = "Name: " + str(self.request.user) + "\nItems:\n" + my_items + "\nTotal Price: Rs." + str(total_price)
                message2 = "Your order of items:\n" + my_items + "\nTotal Price: Rs." + str(total_price) + "\nYou can contact us on sales@organicpasal.com"
                try:
                    send_mail(subject, message, EMAIL_HOST_USER, [EMAIL_HOST_USER], fail_silently=False)
                except BadHeaderError:
                    return Response({"message": "Invalid header found."}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    print(e)
                try:
                    send_mail(subject, message2, EMAIL_HOST_USER, [
                                self.request.user.email], fail_silently=False)
                except BadHeaderError:
                    return Response({"message": "Invalid header found."}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    print(e)

                return Response({"message": "Your order was successful!"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Error while validating form data. Please try again..."}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({"message": "You do not have an active order"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



def save_order_db(order, total_price, address):
    order.ordered_date = timezone.now()
    order.total_price = total_price
    order.shipping_address = Address.objects.filter(id=address['id']).first()
    order.save()

    order_items = order.items.all()
    order_items.update(ordered=True)
    total_profit_loss = 0
    for item in order_items:

        total_profit_loss += item.profit_loss
        item.save()

    order.ordered = True
    order.status = 0
    order.ref_code = create_ref_code()
    order.total_profit_loss = total_profit_loss
    order.save()


class HomeView(APIView):

    def get(self, *args, **kwargs):
        items = Product.objects.filter(is_active=True).order_by('-id')
        categories = Category.objects.filter(is_active=True)
        posts = Post.objects.filter(status=1).order_by('-created_on')

        items_serializer = ProductSerializer(items, many=True).data
        categories_serialzer =CategorySerializer(categories, many=True).data
        posts_serializer = PostSerializer(posts,many=True).data
        context = {
            'all_popular_items': items_serializer,
            'categories': categories_serialzer,
            'blogs': posts_serializer,
        }
        return Response(context,status=status.HTTP_200_OK)


class OrderSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.filter(user=self.request.user, ordered=False).first()
            context = {
                'order': OrderSerializer(order).data,
                'subtotal': order.get_subtotal() if order else 0,
                'total': order.get_total() if order else 0,
            }
            return Response(context, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": "Something went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class WishlistView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, *args, **kwargs):
        try:
            wishlist = Wishlist.objects.filter(user=self.request.user)
            context = {
                'wishlist': WishlistSerializer(wishlist, many=True).data,
            }
            return Response(context, status=status.HTTP_200_OK)
        except:
            return Response({"message": "Something went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ItemDetailView(APIView):

    def get(self, *args, **kwargs):
        item = Product.objects.get(slug=self.kwargs['slug'])
        items = Product.objects.all()
        reviews = Review.objects.filter(item=Product)
        item_serializer = ProductSerializer(Product, context={'user_id': self.request.user.id}).data
        reviews_serializer = ReviewSerializer(reviews, many=True).data

        context = {
            'item':  item_serializer,
            'reviews': reviews_serializer,
        }
        return Response(context, status=status.HTTP_200_OK)


class ShopDetailView(APIView):

    def get(self, *args, **kwargs):
        all_items = Product.objects.filter(is_active=True).order_by('-id')
        categories = Category.objects.filter(is_active=True)
        price_range_min = Product.objects.all().aggregate(Min('price'))
        price_range_max = Product.objects.all().aggregate(Max('price'))
        price_range = {'min': price_range_min, 'max': price_range_max}

        all_items_serializer = ProductSerializer(all_items, many=True, context={'user_id': self.request.user.id}).data
        categories_serializer = CategorySerializer(categories, many=True).data
        context = {
            'items':  all_items_serializer,
            'categories':  categories_serializer,
            'price_range': price_range,
        }
        return Response(context, status=status.HTTP_200_OK)


class CategoryDetailView(APIView):

    def get(self, *args, **kwargs):
        
        category = get_object_or_404(Category, slug=self.kwargs['slug'])

        all_items = Product.objects.filter(is_active=True, category=category).order_by('-id')
        categories = Category.objects.filter(is_active=True)
        price_range_min = Product.objects.all().aggregate(Min('price'))
        price_range_max = Product.objects.all().aggregate(Max('price'))
        price_range = {'min': price_range_min, 'max': price_range_max}
       
       

        all_items_serializer = ProductSerializer(all_items, many=True, context={'user_id': self.request.user.id}).data
        categories_serializer = CategorySerializer(categories, many=True).data

        context = {
            'items':  all_items_serializer,
            'categories':  categories_serializer,
            
            'price_range': price_range,
            'category': CategorySerializer(category).data,
        }
        return Response(context, status=status.HTTP_200_OK)


class SearchView(APIView):

    def post(self, *args, **kwargs):
        search = self.request.data['search_q']
        results = Product.objects.filter(Q(name__icontains=search), is_active=True)
        categories = Category.objects.filter(is_active=True)
        query = search
        price_range_min = Product.objects.all().aggregate(Min('price'))
        price_range_max = Product.objects.all().aggregate(Max('price'))
        price_range = {'min': price_range_min, 'max': price_range_max}
       
        results_serializer = ProductSerializer(results, many=True, context={'user_id': self.request.user.id}).data
        categories_serializer = CategorySerializer(categories, many=True).data
        
        context = {
            'query': query,
            'items': results_serializer,
            'categories': categories_serializer,
            'price_range': price_range,
           
        }
        
        return Response(context, status=status.HTTP_200_OK)


class AboutView(APIView):
 
    def get(self, *args, **kwargs):
        categories = Category.objects.filter(is_active=True)
        
        categories_serializer = CategorySerializer(categories, many=True).data
        context = {
            'categories': categories_serializer,
           
        }
        
        return Response(context, status=status.HTTP_200_OK)



class ContactView(APIView):

   
    def get(self, *args, **kwargs):
        categories = Category.objects.filter(is_active=True)
       

        categories_serializer = CategorySerializer(categories, many=True).data
        context = {
            'categories': categories_serializer,
            
        }
        
        return Response(context, status=status.HTTP_200_OK)


@api_view(['POST'])
@csrf_exempt
@permission_classes([permissions.IsAuthenticated])
def add_to_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
        ordered_date=timezone.now()
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
       
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            return Response({"message": "This item quantity was updated."}, status=status.HTTP_200_OK)
        else:
            order.items.add(order_item)
            return Response({"message": "This item was added to your cart."}, status=status.HTTP_200_OK)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        return Response({"message": "This item was added to your cart."}, status=status.HTTP_200_OK)


@api_view(['POST'])
@csrf_exempt
@permission_classes([permissions.IsAuthenticated])
def add_items_to_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    quantity = request.data['quantity']
    size = request.data['size']
    color = request.data['color']
    if int(quantity) > 0:
        if int(quantity) <= item.stock_count:
            order_item, created = OrderItem.objects.get_or_create(
                item=item,
                user=request.user,
                ordered=False
            )
            order_qs = Order.objects.filter(user=request.user, ordered=False)
            if order_qs.exists():
                order = order_qs[0]
                
                if order.items.filter(item__slug=item.slug).exists():
                    order_item.quantity = order_item.quantity + int(quantity)
                    order_item.save()
                    return Response({"message": "This order item was updated."}, status=status.HTTP_200_OK)
                else:
                    order_item.quantity = int(quantity)
                    order_item.save()
                    order.items.add(order_item)
                    return Response({"message": "This item was added to your cart."}, status=status.HTTP_200_OK)
            else:
                ordered_date = timezone.now()
                order = Order.objects.create(user=request.user, ordered_date=ordered_date)
                order_item.quantity = int(quantity)
                order_item.save()
                order.items.add(order_item)
                return Response({"message": "This item was added to your cart."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "The quantity cannot be more than "+str(item.stock_count)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message": "The quantity cannot be less than zero."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@csrf_exempt
@permission_classes([permissions.IsAuthenticated])
def add_single_item_to_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]

        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()

            my_items = OrderItem.objects.filter(user=request.user, ordered=False)
            data = serializers.serialize('json', my_items)
            order_items = json.loads(data)
            my_order = Order.objects.filter(user=request.user, ordered=False)
            data2 = serializers.serialize('json', my_order)
            my_order = json.loads(data2)

            # messages.success(request, "This item quantity was updated.")
            # return redirect("order-cart")
            return Response({'success': 'Success', 'order_items': order_items, 'my_order': my_order}, status=status.HTTP_200_OK)
        else:
            order.items.add(order_item)
            return Response({"message": "This item was added to your cart."}, status=status.HTTP_200_OK)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        return Response({"message": "This item was added to your cart."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@csrf_exempt
@permission_classes([permissions.IsAuthenticated])
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)

            my_items = OrderItem.objects.filter(
                user=request.user, ordered=False)
            data = serializers.serialize('json', my_items)
            order_items = json.loads(data)
            return Response({'status': 'Success', 'order_items': order_items}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "This item was not in your cart."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message": "You do not have an active order."}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@csrf_exempt
@permission_classes([permissions.IsAuthenticated])
def remove_from_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()

            return Response({"message": "This item was removed from your cart."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "This item was not in your cart."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message": "You do not have an active order."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def add_to_wishlist(request, slug):
    item = get_object_or_404(Product, slug=slug)
    Wishlist.objects.get_or_create(item=item, user=request.user)
    count = Wishlist.objects.filter(user=request.user).count()
    return JsonResponse({"count": count, "status": 200, "message": "Successfully Added To The Wishlist."})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def remove_from_wishlist(request, slug):
    item = get_object_or_404(Product, slug=slug)
    wishlist_item = Wishlist.objects.filter(
        item=item,
        user=request.user
    )
    if wishlist_item.exists():
        wishlist_item.delete()
        return Response({"message": "This item is deleted from Wishlist."}, status=status.HTTP_200_OK)
    else:
        return Response({"message": "This item is not available in Wishlist."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@csrf_exempt
def contact_form(request):
    if request.method == "POST":
        try:
            name = request.data['name']
            email = request.data['email']
            subject = request.data['subject']
            message = request.data['message']
            contact_us = Contact.objects.create(name=name, email=email, subject=subject, message=message)

            subject = subject + " - Contact Fashion Fit"
            message = "Name: " + name + "\nEmail: " + email + "\nMessage: " + message
            try:
                send_mail(subject, message, email, [EMAIL_HOST_USER], fail_silently=False)
            except BadHeaderError:
                return Response({"message": "Invalid header found."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Contact form submitted."}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"message": "Required fields missing."}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "Something went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@csrf_exempt
def product_review(request, slug):
    if request.method == "POST":
        try:
            username = request.data['username']
            rating = request.data['rating']
            description = request.data['description']

            user = User.objects.get(username=username)
            item = Product.objects.get(slug=slug)
            Review.objects.create(user=user, item=item, rating=rating, description=description)

            return Response({"message": "You review has been submitted."}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": "Something went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class BlogsView(APIView):

   
    def get(self, *args, **kwargs):
        posts = Post.objects.filter(status=1).order_by('-created_on')

        categories = Category.objects.filter(is_active=True)
       
        
        posts_serializer = PostSerializer(posts, many=True).data
        categories_serializer = CategorySerializer(categories, many=True).data
       
        context = {
            'blogs': posts_serializer,
            'categories': categories_serializer,
            
        }
        
        return Response(context, status=status.HTTP_200_OK)



class BlogView(APIView):

   
    def get(self, *args, **kwargs):
        posts = Post.objects.filter(slug=kwargs['slug']).first()
        categories = Category.objects.filter(is_active=True)
        
        posts_serializer = PostSerializer(posts).data
        categories_serializer = CategorySerializer(categories, many=True).data
        context = {
            'blog': posts_serializer,
            'categories': categories_serializer,
        }
        
        return Response(context, status=status.HTTP_200_OK)



class OrderConfirmation(APIView):

    def get(self, *args, **kwargs):
        categories = Category.objects.filter(is_active=True)
        
        
        categories_serializer = CategorySerializer(categories, many=True).data
       
        context = {
            'categories': categories_serializer,
            
        }
        
        return Response(context, status=status.HTTP_200_OK)


class ThankYou(APIView):

    
    def get(self, *args, **kwargs):
        categories = Category.objects.filter(is_active=True)
        
        
        categories_serializer = CategorySerializer(categories, many=True).data
        context = {
            'categories': categories_serializer,
        }
        
        return Response(context, status=status.HTTP_200_OK)



class DashboardPage(APIView):

    def get(self, *args, **kwargs):
        profile = self.request.user
        categories = Category.objects.filter(is_active=True)
        
        
        categories_serializer = CategorySerializer(categories, many=True).data
       
        context = {
            'profile': profile,
            'categories': categories_serializer,
            
        }
        
        return Response(context, status=status.HTTP_200_OK)



class OrdersViewPage(APIView):

    
    def get(self, *args, **kwargs):
        orders = Order.objects.filter(user=self.request.user, ordered=True).order_by('-id')

        orders_serializer = OrderSerializer(orders, many=True).data
        context = {
            'orders': orders_serializer,
        }
        
        return Response(context, status=status.HTTP_200_OK)



class CategoriesView(APIView):

    def get(self, *args, **kwargs):
        categories = Category.objects.filter(is_active=True)
        
        
        
        categories_serializer = CategorySerializer(categories, many=True).data
        
        
        context = {
            'categories': categories_serializer,
             
        }
        
        return Response(context, status=status.HTTP_200_OK)


class AddressView(APIView):
    
    def get(self, *args, **kwargs):
        try:
            addresses = Address.objects.filter(user=self.request.user)

            address_serializer = AddressSerializer(addresses, many=True).data
            context = {
                'addresses': address_serializer,
            }
            return Response(context, status=status.HTTP_200_OK)
        except:
            return Response({"message": "Something went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def post(self, *args, **kwargs):
        try:
            full_name = self.request.data['full_name']
            phone_number = self.request.data['phone_number']
            street_address = self.request.data['street_address']
            apartment_address = self.request.data['apartment_address']
            default = self.request.data['default']

            if default == "true":
                addresses = Address.objects.filter(user=self.request.user, default=True).first()
                if addresses:
                    addresses.default = False
                    addresses.save()
            
            address = Address()
            address.user = self.request.user
            address.full_name = full_name
            address.phone_number = phone_number
            address.street_address = street_address
            address.apartment_address = apartment_address
            addresses = Address.objects.filter(user=self.request.user).first()
            if addresses:
                address.default = True if (default == "true") else False
            else:
                address.default = True

            address.save()

            return Response({"message": "Your address was successful added!", "address": address}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UpdateAddressView(APIView):
   
    def get(self, *args, **kwargs):
        try:
            address = Address.objects.get(id=kwargs['address_id'])

            address_serializer = AddressSerializer(address).data
            context = {
                'address': address_serializer,
            }
            return Response(context, status=status.HTTP_200_OK)
        except:
            return Response({"message": "Something went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def patch(self, *args, **kwargs):
        try:
            address_id = kwargs['address_id']
            full_name = self.request.data['full_name']
            phone_number = self.request.data['phone_number']
            street_address = self.request.data['street_address']
            apartment_address = self.request.data['apartment_address']
            default = self.request.data['default']

            if default == "true":
                addresses = Address.objects.filter(user=self.request.user, default=True).first()
                if addresses:
                    addresses.default = False
                    addresses.save()
            
            address = Address.objects.get(id=address_id)
            address.full_name = full_name
            address.phone_number = phone_number
            address.street_address = street_address
            address.apartment_address = apartment_address
            address.default = True if (default == "true") else False
            address.save()

            return Response({"message": "Your address was successful updated!"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def delete(self, *args, **kwargs):
        try:
            address = Address.objects.get(id=kwargs['address_id'])
            address.delete()

            return Response({"message": "Your address was successful removed!"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  

