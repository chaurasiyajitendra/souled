from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("users/",views.users, name="users"),
    path("products/", views.products, name="products"),
    path("orders/",views.orders,name="getOrders"),
    path("users/delete/<int:id>/", views.deleteUser, name="deleteUser"),
    path("products/add/", views.addProduct, name="addProduct"),
    path("products/edit/<int:id>/", views.editProduct, name="editProduct"),
    path("products/delete/<int:id>/", views.deleteProduct, name="deleteProduct"),
    path("products/activate/<int:id>/",views.activateProduct,name="activateProduct"),
    path("orders/edit/<int:id>/",views.editOrder,name="editOrder"),
    path("orders/delete/<int:id>/",views.deleteOrder,name="deleteOrder"),
    path("orders/view/<int:id>/",views.viewOrder,name="viewOrder"),
    path("get-subcategories/<int:category_id>/",views.getSubcategories,name="getSubcategories"),
    path("get-childcategories/<int:subcategory_id>/",views.getChildcategories,name="getChildcategories"),
]