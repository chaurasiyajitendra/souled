from django.db import models
from django.utils.text import slugify



# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=40)
    username = models.CharField(unique=True,max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=45)
    profile = models.FileField(upload_to="profile",blank=True,null=True)
    phone = models.CharField(max_length=10,null=True,blank=True)
    address = models.TextField(blank=True)
    createAt = models.DateField(auto_now_add=True,null=True,blank=True)
    loginAt = models.DateField(auto_now=True,null=True,blank=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name="subcategories")
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ChildCategory(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE,related_name="childcategories")
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(models.Model):
    name = models.CharField(max_length=100)
    detail = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    subCategory = models.ForeignKey(SubCategory,on_delete=models.CASCADE)
    childCategory = models.ForeignKey(ChildCategory,on_delete=models.CASCADE)
    image = models.FileField(upload_to="product",blank=True,null=True)
    createdAt = models.DateField(auto_now_add=True,null=True,blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        return self.product.price * self.quantity


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, default="COD")
    status = models.CharField(max_length=20,default="Pending")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class Payment(models.Model):
    order = models.ForeignKey("Order",on_delete=models.CASCADE,related_name="payments")
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    amount = models.IntegerField()  
    status = models.CharField(max_length=20, default="Created")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.razorpay_order_id