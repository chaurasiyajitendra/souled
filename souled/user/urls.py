from django.urls import path
from . import views

urlpatterns = [

    #Testing Routes 
    path("test/",views.test,name="test"),
    path("testwithid/<int:id>/",views.testing,name="testingWithId"),

    path("",views.index,name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/",views.logout,name="logout"),
    path("profile/",views.profile,name="profile"),
    path("edit-profile/",views.editProfile,name="editProfile"),
    path("change-password/",views.changePassword,name="changePassword"),
    path("about/" ,views.about,name="about"),
    path("contact/" ,views.contact,name="contact"),
    path("cart/" ,views.cart,name="cart"),
    path("add-to-cart/<int:product_id>/", views.addToCart, name="addToCart"),
    path("increase-cart/<int:productId>/", views.increaseCart, name="increaseCart"),
    path("decrease-cart/<int:productId>/", views.decreaseCart, name="decreaseCart"),
    path("removefromcart/<int:productId>/", views.removeFromCart, name="removeFromCart"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("add-to-wishlist/<int:product_id>/",views.addToWishlist,name="addToWishlist"),
    path("remove-wishlist/<int:id>/",views.removeWishlist,name="removeWishlist"),
    path("buy-now/<int:id>/",views.buy_now,name="buyNow"),
    path("orders/",views.orders,name="orders"),
    path("checkout/", views.checkout, name="checkout"),
    path("pay/<int:order_id>/",views.payment_page,name="payment_page"),
    path("payment-success/",views.payment_success,name="payment_success"),
    path("payment-failed/",views.payment_failed,name="payment_failed"),
    path("order-success/<int:id>/",views.orderSuccess,name="orderSuccess"),
    path("product/<int:id>/", views.productDetail, name="product_detail"),
    path("search/",views.search_products,name="search"),
    path("<slug:category>/",views.category_products,name="category"),
    path("<slug:category>/<slug:subcategory>/<slug:child>/",views.product_list,name="product_list"),
    path("<slug:category>/<slug:subcategory>/",views.subcategory_products,name="subcategory",),
    path("<slug:category>/<slug:subcategory>/<slug:child>/",views.childcategory_products,name="childcategory",),
]