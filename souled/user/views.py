from django.shortcuts import render,redirect,get_object_or_404
from .models import User, Product, Category, SubCategory, ChildCategory,Cart,Wishlist,Order,Payment
from django.contrib.auth.hashers import make_password, check_password
from decimal import Decimal
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse



client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


# Create your views here.

def index(req):

    trending_products = Product.objects.order_by("-id").filter(active=True)[:8]

    return render(req, "inde.html", {
        "trending_products": trending_products,
    })


def register(request):
    if "user_id" in request.session:
        return redirect("/");
    if request.method == "POST":
        name = request.POST.get("name")
        username = request.POST.get("username").replace(" ", "")
        email = request.POST.get("email", "").strip().lower()
        password = make_password(request.POST.get("password"))
        phone = request.POST.get("phone")

        if User.objects.filter(email=email).exists():

            return render(request, "register.html", {
                "error": "This email is already registered."
            })

        if User.objects.filter(username=username).exists():

            return render(request, "register.html", {
                "error": "This username is already taken."
            })

        user = User.objects.create(
            name = name,
            username = username,
            email = email,
            password= password,
            phone = phone
        )
        request.session["user_id"] = user.id
        request.session["username"] = user.username
        return redirect("/")

    return render(request, "register.html")

def login(request):
    if "user_id" in request.session:
        return redirect("/");

    if request.method == "POST":

        email = request.POST.get("email").strip().lower()
        password = request.POST.get("password")



        try:
            user = User.objects.get(email=email)

            if check_password(password, user.password):
                request.session["user_id"] = user.id
                request.session["username"] = user.username

                user.loginAt = timezone.now()
                user.save()

                if email == "admin@me.com":
                    return redirect("/director/")

                return redirect("/")

            return render(request, "login.html", {
                "error": "Invalid Email OR Password"
            })

        except User.DoesNotExist:
            return render(request, "login.html", {
                "error": "Invalid Email OR Password"
            })

    return render(request, "login.html")

def logout(req):

    req.session.flush()

    return redirect("/login")

def profile(req):
    return HttpResponse("PROFILE WORKING")


def editProfile(req):
    if "user_id" not in req.session:
        return redirect("/login")

    userId = req.session.get("user_id");
    user = User.objects.filter(id=userId).first()

    if req.method == "POST":
        name = req.POST.get("name")
        username = req.POST.get("username")
        email = req.POST.get("email")
        address = req.POST.get("address")
        profile = req.FILES.get("profile")

        if user.name != name:
            user.name = name
        if user.username != username:
            user.username = username
            req.session["username"] = username

        if user.email != email:
            user.email = email
        if user.address != address:
            user.address = address
        if profile:
            user.profile = profile

        user.save()

        return redirect("/profile")

    return render(req,"editProfile.html")

def changePassword(req):
    userId = req.session.get("user_id")
    user = User.objects.filter(id=userId).first()

    if req.method == "POST":
        oldPassword = req.POST.get("old_password")
        newPassword = req.POST.get("new_password")
        confirmPassword = req.POST.get("confirm_password")

        if check_password(oldPassword ,user.password):

            if check_password(newPassword, user.password):
                return render(req, "changePassword.html", {
                    "err": "New password cannot be the same as the current password."
                })

            if newPassword != confirmPassword:
                return render(req,"changePassword.html",{"err":"New password cannot be the same to confirom password."})

            user.password = make_password(newPassword)
            user.save()
            return render(req,"changePassword.html",{"success": "Password changed successfully."})
        
        else:
            return render(req,"changePassword.html",{"err":"Current password is incorrect."})
    return render(req,"changePassword.html")

def about(req):
    return render(req,"about.html")

def contact(req):
    return render(req,"contact.html")

def search_products(request):

    query = request.GET.get("q", "")

    products = Product.objects.filter(
        name__icontains=query,
        active=True
    )

    return render(request, "products.html", {
        "products": products,
        "search_query": query
    })

def category_products(request, category):
    category_obj = Category.objects.get(slug=category)

    products = Product.objects.filter(
        Q(category=category_obj) &
        Q(active=True)
    )

    return render(request, "products.html", {
        "products": products,
        "category": category_obj,
    })

def subcategory_products(request, category, subcategory):

    category_obj = Category.objects.get(slug=category)
    subcategory_obj = SubCategory.objects.get(
        slug=subcategory,
        category=category_obj
    )
    products = Product.objects.filter(
        Q(subCategory=subcategory_obj)&
        Q(active=True)
    )
    return render(request, "products.html", {
        "products": products,
    })

def childcategory_products(request, id):
    child_category = ChildCategory.objects.get(id=id)

    products = Product.objects.filter(
        Q(childCategory=child_category)&
        Q(active=True)
    )

    return render(request, "products.html", {
        "products": products,
        "child_category": child_category
    })

def product_list(request, category, subcategory, child):


    child_category = ChildCategory.objects.get(
        slug=child,
        subcategory__slug=subcategory,
        subcategory__category__slug=category
    )

    products = Product.objects.filter(
        Q(childCategory=child_category)&
        Q(active=True)
    )

    return render(request, "products.html", {
        "products": products,
        "child_category": child_category,
    })

def productDetail(request, id):

    product = get_object_or_404(Product, id=id)


    child_category = product.childCategory

    related_products = Product.objects.filter(
        childCategory=product.childCategory
    ).exclude(id=product.id)[:4]

    inWhishlist = Wishlist.objects.filter(
        user_id=request.session.get("user_id"),
        product=product
    ).exists()

    return render(request, "productDetail.html", {
        "product": product,
        "related_products": related_products,
        "child_category": child_category,
        "inWishlist": inWhishlist 
    })


def addToWishlist(request, product_id):

    if "user_id" not in request.session:
        return redirect("/login/")

    user = User.objects.get(id=request.session["user_id"])
    product = get_object_or_404(Product, id=product_id)

    Wishlist.objects.get_or_create(
        user=user,
        product=product
    )

    return redirect(request.META.get("HTTP_REFERER", "/"))

def wishlist(request):

    if "user_id" not in request.session:
        return redirect("/login/")

    user = User.objects.get(id=request.session["user_id"])

    wishlist_items = Wishlist.objects.filter(
        user=user
    ).select_related("product")

    return render(request, "wishlist.html", {
        "wishlist_items": wishlist_items
    })

def removeWishlist(request, id):

    if "user_id" not in request.session:
        return redirect("/login/")

    user = User.objects.get(id=request.session["user_id"])

    item = get_object_or_404(
        Wishlist,
        Q(product_id=id) | Q(id=id),
        user=user
    )

    item.delete()   
    return redirect(request.META.get("HTTP_REFERER", "/"))


def addToCart(request, product_id):
    if "user_id" not in request.session:
        return redirect("/login")
    userId = request.session["user_id"]
    user = User.objects.get(id=userId)
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = Cart.objects.get_or_create(user=user, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("/cart/")

def cart(request):
    if "user_id" not in request.session:
        return redirect("/login")
    userId =request.session["user_id"]
    user = User.objects.get(id=userId)

    cart_items = Cart.objects.filter(user=user).select_related("product")

    total = sum(item.subtotal for item in cart_items)

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total": total,
    })

def calculate_cart_total(user_id):
    if not user_id:
        return 0
    
    cart_items = Cart.objects.filter(user_id=user_id)
    return sum(item.product.price * item.quantity for item in cart_items)

def increaseCart(request, productId):
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'User not logged in'}, status=401)

    cart_item = get_object_or_404(Cart, id=productId, user_id=user_id)
    cart_item.quantity += 1
    cart_item.save()

    total = calculate_cart_total(user_id)
    subtotal = cart_item.product.price * cart_item.quantity

    return JsonResponse({
        'status': 'updated',
        'quantity': cart_item.quantity,
        'subtotal': subtotal,
        'total': total
    })

def decreaseCart(request, productId):
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'User not logged in'}, status=401)

    cart_item = get_object_or_404(Cart, id=productId, user_id=user_id)
    is_deleted = False

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        item_qty = cart_item.quantity
        subtotal = cart_item.product.price * cart_item.quantity
    else:
        cart_item.delete()
        is_deleted = True
        item_qty = 0
        subtotal = 0

    total = calculate_cart_total(user_id)

    return JsonResponse({
        'status': 'deleted' if is_deleted else 'updated',
        'quantity': item_qty,
        'subtotal': subtotal,
        'total': total
    })

def removeFromCart(request, productId):
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'User not logged in'}, status=401)

    cart_item = get_object_or_404(Cart, id=productId, user_id=user_id)
    cart_item.delete()

    total = calculate_cart_total(user_id)

    return JsonResponse({
        'status': 'deleted',
        'total': total,
    })

def buy_now(request, id):

    # User login check
    if "user_id" not in request.session:
        return redirect("/login/")

    # Logged-in user
    user = get_object_or_404(
        User,
        id=request.session["user_id"]
    )

    # Product
    product = get_object_or_404(
        Product,
        id=id,
        active=True
    )

    # Quantity
    quantity = int(request.POST.get("quantity", 1))

    # Quantity validation
    if quantity < 1:
        quantity = 1

    # Stock check
    if quantity > product.quantity:
        quantity = product.quantity

    # Total price
    total_price = product.price * quantity

    # POST -> Order create
    if request.method == "POST":

        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        payment_method = request.POST.get("payment", "COD")

        order = Order.objects.create(
            user=user,
            product=product,
            quantity=quantity,
            total_price=total_price,
            full_name=name,
            phone=phone,
            address=address,
            payment_method=payment_method,
            status="Pending"
        )

        return redirect("orderSuccess", id=order.id)

    # GET -> Buy Now page
    return render(request, "buyNow.html", {
        "product": product,
        "quantity": quantity,
        "total_price": total_price,
        "user": user,
    })

def checkout(request):
    if "user_id" not in request.session:
        return redirect("/login/")

    user = User.objects.get(id=request.session["user_id"])
    cart_items = Cart.objects.filter(user=user)

    if not cart_items.exists():
        return redirect("/cart/")

    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    
    shipping = Decimal('0.00')
    discount = Decimal('0.00')

    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        pincode = request.POST.get("pincode")

        payment_method = request.POST.get("payment")
        shipping_method = request.POST.get("shipping")


        if shipping_method == "express":
            shipping = Decimal('99.00')

        total = subtotal + shipping - discount

        item_shipping = shipping / Decimal(cart_items.count())


        for item in cart_items:
            item_total = (item.product.price * item.quantity) + item_shipping
            
            order = Order.objects.create(
                user=user,
                product=item.product,
                quantity=item.quantity,
                total_price=item_total,
                full_name = name,
                address = address,
                phone = phone,
                payment_method = payment_method
            )

        cart_items.delete()

        return redirect("payment_page", order_id=order.id)


    total = subtotal + shipping - discount

    context = {
        "user": user,
        "cart_items": cart_items,
        "subtotal": subtotal,
        "shipping": shipping,
        "discount": discount,
        "total": total,
    }

    return render(request, "checkout.html", context)

def orders(req):
    if "user_id" not in req.session:
        return redirect("/login/")

    userId = req.session["user_id"]
    user = User.objects.get(id=userId)
    
    user_orders = Order.objects.filter(user=user).order_by("-created_at")

    return render(req, "myOrder.html", {"orders": user_orders})


def payment_page(request, order_id):

    if "user_id" not in request.session:
        return redirect("/login/")

    user = get_object_or_404(
        User,
        id=request.session["user_id"]
    )

    order = get_object_or_404(
        Order,
        id=order_id,
        user=user
    )

    # Razorpay amount paise me leta hai
    amount = int(order.total_price * 100)

    # Razorpay order create
    razorpay_order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    # Payment database me create
    Payment.objects.create(
        order=order,
        razorpay_order_id=razorpay_order["id"],
        amount=order.total_price,
    )

    return render(request, "paymentPage.html", {
        "order": order,
        "order_id": razorpay_order["id"],
        "amount": amount,
        "key_id": settings.RAZORPAY_KEY_ID,
    })


@csrf_exempt
def payment_success(request):

    if request.method != "POST":
        return redirect("/")

    payment_id = request.POST.get("razorpay_payment_id")
    razorpay_order_id = request.POST.get("razorpay_order_id")
    signature = request.POST.get("razorpay_signature")

    try:

        payment = Payment.objects.select_related("order").get(
            razorpay_order_id=razorpay_order_id
        )

        # Razorpay signature verification
        params = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature
        }

        client.utility.verify_payment_signature(params)

        # Payment update
        payment.razorpay_payment_id = payment_id
        payment.razorpay_signature = signature
        payment.status = "Success"
        payment.save()

        # Order update
        order = payment.order
        order.status = "Confirmed"
        order.save()

        return render(request, "orderSuccess.html", {
            "order": order,
            "amount": payment.amount,
            "payment_id": payment_id,
            "order_id": razorpay_order_id,
        })

    except razorpay.errors.SignatureVerificationError:

        return JsonResponse({
            "status": "error",
            "message": "Payment verification failed."
        }, status=400)

    except Payment.DoesNotExist:

        return JsonResponse({
            "status": "error",
            "message": "Payment record not found."
        }, status=404)

@csrf_exempt
def payment_failed(request):

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Invalid request"
        }, status=400)

    try:

        razorpay_order_id = request.POST.get(
            "razorpay_order_id"
        )

        if not razorpay_order_id:
            return JsonResponse({
                "status": "error",
                "message": "Razorpay order ID missing"
            }, status=400)

        payment = Payment.objects.select_related("order").get(
            razorpay_order_id=razorpay_order_id
        )

        # Payment failed
        payment.status = "Failed"
        payment.save()

        # Order cancel
        order = payment.order
        order.status = "Cancelled"
        order.save()

        return JsonResponse({
            "status": "success",
            "message": "Payment failed and order cancelled."
        })

    except Payment.DoesNotExist:

        return JsonResponse({
            "status": "error",
            "message": "Payment record not found."
        }, status=404)

def orderSuccess(request, id):

    order = get_object_or_404(
        Order.objects.select_related("product"),
        id=id
    )

    return render(request, "orderSuccess.html", {
        "order": order
    })