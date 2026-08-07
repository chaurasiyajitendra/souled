from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("users/",views.users, name="users"),
    path("products/", views.products, name="products"),
    path("orders/",views.orders,name="getOrders")
]