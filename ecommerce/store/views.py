from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
import datetime
import json 
from .models import *
from .utils import cookieCart 
from .utils import cartData
from .utils import guestOrder
from django.contrib.auth.forms import UserCreationForm
from .forms import OrderForm, CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout 
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
# We want to render our store templates, to get an HttpResponse object with rendered text

def store(request):
    
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    
    products = Product.objects.all()
    context = {'products' : products, 'cartItems' : cartItems}
    return render(request, 'store/store.html', context)

def cart(request): 

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'items' : items, 'order' : order, 'cartItems' : cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items' : items, 'order' : order, 'cartItems' : cartItems}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)
 
def processOrder(request):
     transaction_id = datetime.datetime.now().timestamp()
     data = json.loads(request.body)

     if request.user.is_authenticated:
          customer = request.user.customer
          order, created  = Order.objects.get_or_create(customer = customer, complete = False)
     else:
          customer, order = guestOrder(request, data)
     total = float(data['form']['total'])
     order.transaction_id = transaction_id
     if total == order.get_cart_total:
         order.complete = True
     order.save()

     if order.shipping == True:
            ShippingAddress.objects.create(
                    customer = customer,
                    order = order, 
                    address = data ['shipping']['address'],
                    city = data['shipping']['city'],
                    state = data['shipping']['state'],
                    zipcode = data['shipping']['zipcode'],
               )
     return JsonResponse('Payment Complete!', safe = False) 


def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            name = form.cleaned_data.get('name')
            customer = Customer.objects.create(
                user=user,
                name=name,
                email=email,
            )
            messages.success(request, 'Account was successfully created! Welcome ' + username)
            return redirect('login')
    context = {'form': form}
    return render(request, 'accounts/register.html', context)

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        customer = authenticate(request, username=username, password=password)

        if customer is not None:
            try:
                customer = customer.customer
            except ObjectDoesNotExist:
                messages.warning(request, 'Your account does not have a related customer object.')
            else:
                login(request, customer)
                return redirect('store')
        else:
            messages.warning(request, 'Invalid login credentials.')

    context = {}
    return render(request, 'accounts/login.html', context)