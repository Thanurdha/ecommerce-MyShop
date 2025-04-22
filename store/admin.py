from django.contrib import admin
from .models import Category, Product
from .models import Review

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Review)
