from django.urls import path
from django.urls import path,include 
from . import views


# runs through each url pattern and stop at the first one that matches the requested URL

urlpatterns = [
    path('', views.store, name = "store"),
    
    path('checkout/', views.checkout, name = "checkout"),
    
    path('cart/', views.cart, name = "cart"), 

    path('update_item/' , views.updateItem, name = "update_item"),

    path('process_order/' , views.processOrder, name = "process_order"),

    path('register/' , views.registerPage, name = 'register'),

    path('login/', views.loginPage, name = "login"),
]