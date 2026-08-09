from .models import Category,User, Cart, Wishlist

def global_data(request):

    user = None

    cart_count = 0
    wishlist_count = 0

    userId = request.session.get("user_id")

    if userId:

        user = User.objects.filter(id=userId).first()

        if user:

            cart_count = sum(cart.quantity for cart in Cart.objects.filter(user=user))

            wishlist_count = Wishlist.objects.filter(user=user).count()

    return {

        "categories": Category.objects.prefetch_related(
            "subcategories__childcategories"
        ),

        "user": user,

        "is_login": "username" in request.session,

        "cart_count": cart_count,

        "wishlist_count": wishlist_count,
    }