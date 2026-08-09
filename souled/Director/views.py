from django.shortcuts import render,redirect, get_object_or_404
from django.db.models import Sum
from user.models import User,Order,Product,Category, SubCategory, ChildCategory
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from functools import wraps


# Create your views here.

def admin_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if "user_id" not in request.session:
            return redirect("/login/")


        user = User.objects.filter(
            id=request.session["user_id"]
        ).first()

        
        if not user:
            request.session.flush()
            return redirect("/login/")

        
        if user.email.lower() != "admin@me.com":
            return redirect("/")

        return view_func(request, *args, **kwargs)

    return wrapper

@admin_required
def index(request):

    users = User.objects.all()
    products = Product.objects.all()
    orders = Order.objects.all()
    total_revenue = (Order.objects.aggregate(total=Sum("total_price"))["total"] or 0)


    return render(request, 'index.html',{"users":users,"products":products,"orders":orders,"revenue":total_revenue})


@admin_required
def getSubcategories(request, category_id):

    subcategories = SubCategory.objects.filter(
        category_id=category_id
    )

    data = []

    for subcategory in subcategories:

        data.append({
            "id": subcategory.id,
            "name": subcategory.name
        })

    return JsonResponse(data, safe=False)

@admin_required
def getChildcategories(request, subcategory_id):

    childcategories = ChildCategory.objects.filter(
        subcategory_id=subcategory_id
    )

    data = []

    for childcategory in childcategories:

        data.append({
            "id": childcategory.id,
            "name": childcategory.name
        })

    return JsonResponse(data, safe=False)


@admin_required
def users(request):

    users = User.objects.all().order_by("-id")

    today = timezone.now().date()

    active_users = User.objects.exclude(loginAt=None).count()

    today_users = User.objects.filter(createAt=today).count()

    online_users = User.objects.exclude(loginAt=None).count()

    context = {
        "users": users,
        "active_users": active_users,
        "today_users": today_users,
        "online_users": online_users,
    }

    return render(request, "users.html", context)

@admin_required
def deleteUser(request, id):

    user = get_object_or_404(User, id=id)

    user.delete()

    return redirect("users")

@admin_required
def products(request):

    products = Product.objects.select_related(
        "category",
        "subCategory",
        "childCategory"
    ).order_by("-id")

    today = timezone.now().date()

    context = {
        "products": products,
        "total_products": Product.objects.count(),
        "today_products": Product.objects.filter(createdAt=today).count(),
        "in_stock": Product.objects.filter(quantity__gt=0).count(),
        "out_of_stock": Product.objects.filter(Q(quantity=0)|Q(active=False) ).count(),
    }

    return render(request, "viewProducts.html", context)

@admin_required
def addProduct(request):

    categories = Category.objects.all()

    if request.method == "POST":

        Product.objects.create(
            name=request.POST.get("name"),
            detail=request.POST.get("detail"),
            price=request.POST.get("price"),
            quantity=request.POST.get("quantity"),
            category_id=request.POST.get("category"),
            subCategory_id=request.POST.get("subcategory"),
            childCategory_id=request.POST.get("childcategory"),
            image=request.FILES.get("image")
        )

        return redirect("products")

    return render(request, "addProduct.html", {
        "categories": categories
    })

@admin_required
def editProduct(request, id):

    product = get_object_or_404(Product, id=id)

    categories = Category.objects.all()
    subcategories = SubCategory.objects.filter(
        category=product.category
    )
    childcategories = ChildCategory.objects.filter(
        subcategory=product.subCategory
    )

    if request.method == "POST":

        product.name = request.POST.get("name")
        product.detail = request.POST.get("detail")
        product.price = request.POST.get("price")
        product.quantity = request.POST.get("quantity")

        product.category_id = request.POST.get("category")
        product.subCategory_id = request.POST.get("subcategory")
        product.childCategory_id = request.POST.get("childcategory")

        if request.FILES.get("image"):
            product.image = request.FILES.get("image")

        product.save()

        return redirect("products")

    return render(request, "editProduct.html", {
        "product": product,
        "categories": categories,
        "subcategories": subcategories,
        "childcategories": childcategories,
    })


@admin_required
def deleteProduct(request, id):

    product = get_object_or_404(Product, id=id)

    product.active = False
    product.save()

    return redirect("products")

@admin_required
def activateProduct(request, id):

    product = get_object_or_404(Product, id=id)

    product.active = True
    product.save()

    return redirect("products")

@admin_required
def orders(request):

    orders = (
        Order.objects
        .select_related("user", "product")
        .order_by("-id")
    )

    today = timezone.now().date()

    context = {
        "orders": orders,
        "total_orders": Order.objects.count(),
        "today_orders": Order.objects.filter(created_at__date=today).count(),
        "pending_orders": Order.objects.filter(status="Pending").count(),
        "delivered_orders": Order.objects.filter(status="Delivered").count(),
    }

    return render(request, "orders.html", context)

@admin_required
def editOrder(request, id):

    order = get_object_or_404(Order, id=id)

    users = User.objects.all()
    products = Product.objects.all()

    if request.method == "POST":

        order.user_id = request.POST.get("user")
        order.product_id = request.POST.get("product")
        order.quantity = request.POST.get("quantity")
        order.total_price = request.POST.get("total_price")

        order.full_name = request.POST.get("full_name")
        order.phone = request.POST.get("phone")
        order.address = request.POST.get("address")
        order.payment_method = request.POST.get("payment_method")
        order.status = request.POST.get("status")

        order.save()

        return redirect("getOrders")

    return render(request, "editOrder.html", {
        "order": order,
        "users": users,
        "products": products,
    })

@admin_required
def deleteOrder(request, id):

    order = get_object_or_404(Order, id=id)

    order.delete()

    return redirect("getOrders")

@admin_required
def viewOrder(request, id):

    order = get_object_or_404(
        Order.objects.select_related(
            "user",
            "product",
            "product__category"
        ),
        id=id
    )

    return render(request, "viewOrder.html", {
        "order": order
    })