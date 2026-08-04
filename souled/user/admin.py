from django.contrib import admin
from .models import Category, SubCategory, ChildCategory,Product,User

# Register your models here.
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(ChildCategory)
admin.site.register(Product)
admin.site.register(User)


