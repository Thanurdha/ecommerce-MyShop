from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Category, CartItem, Order

# Home page
def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories,
    })

# Products by category
def category_products(request, category_id):
    selected_category = Category.objects.get(id=category_id)
    products = Product.objects.filter(category=selected_category)
    return render(request, 'store/category_products.html', {
        'category': selected_category,
        'products': products
    })

# Add to cart
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('view_cart')

# View cart
@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in cart_items)
    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

# ✅ Remove from cart
@login_required
def remove_from_cart(request, product_id):
    cart_item = CartItem.objects.filter(user=request.user, product_id=product_id).first()
    if cart_item:
        cart_item.delete()
    return redirect('view_cart')

# Checkout page
@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if request.method == 'POST':
        for item in cart_items:
            Order.objects.create(
                user=request.user,
                product=item.product,
                quantity=item.quantity
            )
        cart_items.delete()
        return redirect('thank_you')
    total = sum(item.subtotal() for item in cart_items)
    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'total': total
    })

# Thank you page
@login_required
def thank_you(request):
    order_summary = request.session.get('order_summary', [])
    total = request.session.get('order_total', 0)

    # Optionally clear session data after showing once
    request.session.pop('order_summary', None)
    request.session.pop('order_total', None)

    return render(request, 'store/thankyou.html', {
        'cart_items': order_summary,
        'total': total
    })

# Order history
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    return render(request, 'store/order_history.html', {
        'orders': orders
    })

# About page
def about(request):
    return render(request, 'store/about.html')


# Payment page
@login_required
def payment_page(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in cart_items)

    if request.method == 'POST':
        # Move cart items to Order model
        for item in cart_items:
            Order.objects.create(
                user=request.user,
                product=item.product,
                quantity=item.quantity
            )

        # Save cart data in session to show in thank you
        request.session['order_summary'] = [
            {
                'name': item.product.name,
                'quantity': item.quantity,
                'subtotal': float(item.subtotal())
            } for item in cart_items
        ]
        request.session['order_total'] = float(total)

        # Clear cart
        cart_items.delete()

        return redirect('thank_you')

    return render(request, 'store/payment.html', {
        'cart_items': cart_items,
        'total': total
    })


def todays_deals(request):
    deal_products = Product.objects.filter(is_deal=True)
    return render(request, 'store/todays_deals.html', {
        'products': deal_products
    })

def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    deals = Product.objects.filter(is_deal=True)[:5]  # show top 5 deals
    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories,
        'deals': deals,
    })

