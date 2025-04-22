from django.shortcuts import render
from .models import Product, Category



def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories,
    })
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, CartItem

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('view_cart')
@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in cart_items)
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total})

from django.contrib.auth.decorators import login_required
from .models import CartItem

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in cart_items)
    return render(request, 'store/checkout.html', {'cart_items': cart_items, 'total': total})

@login_required
def thank_you(request):
    return render(request, 'store/thankyou.html')

from .models import Order, CartItem
<<<<<<< HEAD
=======

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
    return render(request, 'store/checkout.html', {'cart_items': cart_items})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    return render(request, 'store/order_history.html', {'orders': orders})

from .models import Product, Category

def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories,
    })

from .models import Product

def category_products(request, category_id):
    selected_category = Category.objects.get(id=category_id)
    products = Product.objects.filter(category=selected_category)
    return render(request, 'store/category_products.html', {
        'category': selected_category,
        'products': products
    })



>>>>>>> dab06a43fb1d3b669d96f5c6bcf57ecc092222ab

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
    return render(request, 'store/checkout.html', {'cart_items': cart_items})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    return render(request, 'store/order_history.html', {'orders': orders})


def about(request):
    return render(request, 'store/about.html')
