from django.db import models
from django.contrib.auth.models import User

# Category of a product
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

# Product available for sale
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/')  # Main image
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_deal = models.BooleanField(default=False)
    likes = models.ManyToManyField(User, related_name='liked_products', blank=True)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.name

# ✅ Additional product images
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.product.name}"

# Cart item linked to a user and product
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.quantity * self.product.price

# A single purchase session (like an invoice)
class OrderGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    address = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'),
                                                      ('Processing', 'Processing'),
                                                      ('Shipped', 'Shipped'),
                                                      ('Delivered', 'Delivered'),
                                                      ('Cancelled', 'Cancelled')],
                              default='Pending')

    def total_amount(self):
        return sum(item.subtotal() for item in self.orderitem_set.all())

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

# Each product within an OrderGroup
class OrderItem(models.Model):
    order_group = models.ForeignKey(OrderGroup, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)  # To preserve price

    def subtotal(self):
        return self.quantity * self.price_at_purchase

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

# Product review by user
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.rating}★ for {self.product.name}"

# Profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images/default.png')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Wishlist
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username}'s Wishlist"


# New Promotion Model
class Promotion(models.Model):
    PROMO_TYPES = [
        ('discount', 'Discount'),
        ('gift', 'Gift'),
    ]

    title = models.CharField(max_length=255)
    promo_type = models.CharField(max_length=20, choices=PROMO_TYPES)
    discount_percentage = models.PositiveIntegerField(default=0, blank=True, null=True)
    message = models.TextField()
    target_category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    free_gift = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    image = models.ImageField(upload_to='promotions/', null=True, blank=True)  # Added image field

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Promotions"


