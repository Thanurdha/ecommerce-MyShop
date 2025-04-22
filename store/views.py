from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Category, CartItem, Order
from django.contrib import messages

# Home page
def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories,
    })

# Products by category
from django.db.models import Avg
from .models import Product

def category_products(request, category_id):
    selected_category = Category.objects.get(id=category_id)
    products = Product.objects.filter(category=selected_category).annotate(avg_rating=Avg('reviews__rating'))
    return render(request, 'store/category_products.html', {
        'category': selected_category,
        'products': products
    })

#Product
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Review
from django.contrib.auth.decorators import login_required

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    size_options = product.get_size_options()
    reviews = product.reviews.all().order_by('-created_at')

    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')
        Review.objects.create(product=product, user=request.user, rating=rating, comment=comment)
        return redirect('product_detail', product_id=product.id)

    return render(request, 'store/product_detail.html', {
        'product': product,
        'size_options': size_options,
        'reviews': reviews,
    })



# Add to cart
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"✅ {product.name} added to your cart!")  # ✅ success message
    return redirect(request.META.get('HTTP_REFERER', 'home'))  # redirect back instead of cart

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

#checkout page
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, CartItem, Order
from django.contrib.auth.decorators import login_required

@login_required
def checkout(request):
    # Check if user came from Buy Now
    buy_now_product_id = request.session.get('buy_now_product_id')
    buy_now_quantity = request.session.get('buy_now_quantity', 1)

    if buy_now_product_id:
        product = get_object_or_404(Product, id=buy_now_product_id)
        total = product.price * int(buy_now_quantity)

        if request.method == 'POST':
            # Create a single order directly
            Order.objects.create(
                user=request.user,
                product=product,
                quantity=buy_now_quantity
            )
            # Clear session after placing order
            del request.session['buy_now_product_id']
            del request.session['buy_now_quantity']
            return redirect('payment')

        return render(request, 'store/checkout.html', {
            'buy_now': True,
            'product': product,
            'quantity': buy_now_quantity,
            'total': total
        })

    # 🛒 If it's a regular cart checkout
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in cart_items)

    if request.method == 'POST':
        for item in cart_items:
            Order.objects.create(
                user=request.user,
                product=item.product,
                quantity=item.quantity
            )

        # Store data in session to use in payment view
        request.session['from_cart_checkout'] = True

        return redirect('payment')

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


from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, CartItem, Order
from django.contrib.auth.decorators import login_required

@login_required
def payment_page(request):
    # Check for Buy Now
    buy_now_product_id = request.session.get('buy_now_product_id')
    buy_now_quantity = int(request.session.get('buy_now_quantity', 1))

    if buy_now_product_id:
        product = get_object_or_404(Product, id=buy_now_product_id)
        subtotal = product.price * buy_now_quantity

        if request.method == 'POST':
            Order.objects.create(
                user=request.user,
                product=product,
                quantity=buy_now_quantity
            )

            # Save to session for thank you page
            request.session['order_summary'] = [{
                'name': product.name,
                'quantity': buy_now_quantity,
                'subtotal': float(subtotal)
            }]
            request.session['order_total'] = float(subtotal)

            # Clear Buy Now session
            del request.session['buy_now_product_id']
            del request.session['buy_now_quantity']

            return redirect('thank_you')

        return render(request, 'store/payment.html', {
            'buy_now': True,
            'product': product,
            'quantity': buy_now_quantity,
            'total': subtotal
        })

    # Else: Cart payment
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in cart_items)

    if request.method == 'POST':
        for item in cart_items:
            Order.objects.create(
                user=request.user,
                product=item.product,
                quantity=item.quantity
            )

        # Save cart summary in session
        request.session['order_summary'] = [
            {
                'name': item.product.name,
                'quantity': item.quantity,
                'subtotal': float(item.subtotal())
            } for item in cart_items
        ]
        request.session['order_total'] = float(total)

        cart_items.delete()
        request.session['from_cart_checkout'] = True
        return redirect('thank_you')

    return render(request, 'store/payment.html', {
        'cart_items': cart_items,
        'total': total
    })
# Fallback
    return redirect('view_cart')

#deals
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

#search
from django.db.models import Q

def search_products(request):
    query = request.GET.get('q', '')
    results = Product.objects.filter(
        Q(name__icontains=query) | Q(category__name__icontains=query)
    ) if query else []

    return render(request, 'store/search_results.html', {
        'query': query,
        'results': results,
    })
#Buy now
@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('qty', 1))
        size = request.POST.get('size', None)  # if you're using sizes
        request.session['buy_now_product_id'] = product.id
        request.session['buy_now_quantity'] = quantity
        request.session['buy_now_size'] = size
        return redirect('checkout')


