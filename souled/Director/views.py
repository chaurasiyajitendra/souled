from django.shortcuts import render
from django.db.models import Sum
from user.models import User,Order,Product
from django.utils import timezone

# Create your views here.
def index(request):

    users = User.objects.all()
    products = Product.objects.all()
    orders = Order.objects.all()
    total_revenue = (Order.objects.aggregate(total=Sum("total_price"))["total"] or 0)


    return render(request, 'index.html',{"users":users,"products":products,"orders":orders,"revenue":total_revenue})

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
        "out_of_stock": Product.objects.filter(quantity=0).count(),
    }

    return render(request, "products.html", context)

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