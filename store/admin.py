from django.contrib import admin
from .models import Category, Product, ProductImage, Review

# Unregister the Product model if it is already registered
try:
    admin.site.unregister(Product)
except admin.sites.NotRegistered:
    pass

# Register Category, Product, and Review models
admin.site.register(Category)
admin.site.register(Review)

# Customizing ProductAdmin to handle additional product images
class ProductImageInline(admin.TabularInline):
    model = ProductImage  # Link to the ProductImage model
    extra = 1  # Number of empty forms to display when adding a product

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]  # Add ProductImage inline to the Product admin
    list_display = ('name', 'price', 'category', 'is_deal')  # Show relevant fields in the list view
    search_fields = ['name', 'category__name']  # Allow search by product name and category
    list_filter = ('category', 'is_deal')  # Filter by category and deal status

# Register the Product model with the custom admin class
admin.site.register(Product, ProductAdmin)

from django.contrib import admin
from .models import OrderGroup

@admin.register(OrderGroup)
class OrderGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'id')
    ordering = ('-created_at',)

