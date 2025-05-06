from collections import defaultdict
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q, Avg
from .models import (
    Product, Category, CartItem, OrderGroup, OrderItem,
    Review, Profile, Wishlist, Promotion
)
from .forms import ProfileForm

#  Home page
def home(request):
    products = Product.objects.select_related('category').all()
    categories = Category.objects.all()
    deals = Product.objects.filter(is_deal=True)[:5]

    categorized_products = defaultdict(list)
    for product in products:
        categorized_products[product.category].append(product)

    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories,
        'deals': deals,
        'categorized_products': categorized_products,
    })

<<<<<<< HEAD
#  Products by category
=======
# ✅ Products by category (with sorting + filtering)
>>>>>>> 52bed887a4e135d47fcc54307fdb3bc735e2e026
def category_products(request, category_id):
    selected_category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=selected_category).annotate(avg_rating=Avg('reviews__rating'))

    # Filtering
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    min_rating = request.GET.get('min_rating')

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if min_rating:
        products = products.filter(avg_rating__gte=min_rating)

    # Sorting
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name_asc':
        products = products.order_by('name')
    elif sort == 'name_desc':
        products = products.order_by('-name')

    return render(request, 'store/category_products.html', {
        'category': selected_category,
        'products': products
    })

#  Add to cart
@login_required
@never_cache
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"✅ {product.name} added to your cart!")
    return redirect(request.META.get('HTTP_REFERER', 'home'))

#  View cart
@login_required
@never_cache
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in cart_items)
    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

#  Remove from cart
@login_required
@never_cache
def remove_from_cart(request, product_id):
    cart_item = CartItem.objects.filter(user=request.user, product_id=product_id).first()
    if cart_item:
        cart_item.delete()
    return redirect('view_cart')

#  Checkout
@login_required
@never_cache
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in cart_items)
    if request.method == 'POST':
        order_group = OrderGroup.objects.create(user=request.user)
        for item in cart_items:
            OrderItem.objects.create(
                order_group=order_group,
                product=item.product,
                quantity=item.quantity,
                price_at_purchase=item.product.price
            )
        cart_items.delete()
        request.session['from_cart_checkout'] = True
        request.session['order_group_id'] = order_group.id
        return redirect('thank_you')
    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'total': total
    })

#  Thank you page
@login_required
@never_cache
def thank_you(request):
    order_group_id = request.session.pop('order_group_id', None)
    if not order_group_id:
        return redirect('home')
    order_group = get_object_or_404(OrderGroup, id=order_group_id, user=request.user)
    order_items = order_group.orderitem_set.all()
    total = order_group.total_amount()
    return render(request, 'store/thankyou.html', {
        'cart_items': order_items,
        'total': total
    })

#  Order history
@login_required
@never_cache
def order_history(request):
    orders = OrderGroup.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_history.html', {
        'orders': orders
    })

#  About page
def about(request):
    return render(request, 'store/about.html')

# ✅ Payment
@login_required
@never_cache
def payment(request):
    buy_now_product_id = request.session.get('buy_now_product_id')
    buy_now_quantity = int(request.session.get('buy_now_quantity', 1))

    if buy_now_product_id:
        product = get_object_or_404(Product, id=buy_now_product_id)
        subtotal = product.price * buy_now_quantity

        if request.method == 'POST' and not request.POST.get('from_checkout'):
            order_group = OrderGroup.objects.create(user=request.user)
            OrderItem.objects.create(
                order_group=order_group,
                product=product,
                quantity=buy_now_quantity,
                price_at_purchase=product.price
            )
            request.session['order_group_id'] = order_group.id
            del request.session['buy_now_product_id']
            del request.session['buy_now_quantity']
            return redirect('thank_you')

        return render(request, 'store/payment.html', {
            'buy_now': True,
            'product': product,
            'quantity': buy_now_quantity,
            'total': subtotal
        })

    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items:
        return redirect('view_cart')

    total = sum(item.subtotal() for item in cart_items)

    if request.method == 'POST':
        if request.POST.get('from_checkout'):
            return render(request, 'store/payment.html', {
                'buy_now': False,
                'cart_items': cart_items,
                'total': total
            })
        else:
            order_group = OrderGroup.objects.create(user=request.user)
            for item in cart_items:
                OrderItem.objects.create(
                    order_group=order_group,
                    product=item.product,
                    quantity=item.quantity,
                    price_at_purchase=item.product.price
                )
            request.session['order_group_id'] = order_group.id
            request.session['order_total'] = float(total)
            cart_items.delete()
            return redirect('thank_you')

    return redirect('checkout')

<<<<<<< HEAD

#  Today's deals
from decimal import Decimal  # Add this import at the top

=======
# ✅ Today's deals
>>>>>>> 52bed887a4e135d47fcc54307fdb3bc735e2e026
def todays_deals(request):
    deal_products = Product.objects.filter(is_deal=True)
    for product in deal_products:
        product.original_price = product.price
        product.deal_price = (product.price * Decimal('0.7')).quantize(Decimal('0.01'))  # 30% discount
    return render(request, 'store/todays_deals.html', {
        'products': deal_products
    })


#  Search products
def search_products(request):
    query = request.GET.get('q', '')
    results = Product.objects.filter(Q(name__icontains=query) | Q(category__name__icontains=query)) if query else []
    return render(request, 'store/search_results.html', {
        'query': query,
        'results': results,
    })

#  Product detail
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all().order_by('-created_at')
    size_options = []
    if product.category.name.lower() == 'clothing':
        size_options = ['S', 'M', 'L', 'XL']
    elif product.category.name.lower() == 'shoes':
        size_options = ['6', '7', '8', '9', '10', '11']

    if request.method == 'POST' and 'rating' in request.POST:
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment', '')
        Review.objects.create(product=product, user=request.user, rating=rating, comment=comment)
        return redirect('product_detail', product_id=product.id)

    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'size_options': size_options
    })

#  Buy now
@login_required
@never_cache
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('qty', 1))
        size = request.POST.get('size', None)
        request.session['buy_now_product_id'] = product.id
        request.session['buy_now_quantity'] = quantity
        request.session['buy_now_size'] = size
        return redirect('payment')
    return redirect('product_detail', product_id=product_id)

#  Signup
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! You are now logged in.')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'store/signup.html', {'form': form})

#  Logout views
@login_required
def logout_confirmation(request):
    return render(request, 'store/logout_confirmation.html')

@never_cache
def logged_out(request):
    return render(request, 'store/logged_out.html')

def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('logged_out')

#  Profile view
@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Profile updated successfully.")
            return redirect('home')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'store/profile.html', {'form': form, 'profile': profile})

#  Wishlist views
@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def remove_from_wishlist(request, product_id):
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect('wishlist')

<<<<<<< HEAD
#  Promotions page (protected by login)
=======
# ✅ Promotions
>>>>>>> 52bed887a4e135d47fcc54307fdb3bc735e2e026
@login_required
def promotions(request):
    left_values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 95]
    duration_values = [8, 10, 12, 14, 9, 11, 13, 15, 10, 12]
    combined_values = zip(left_values, duration_values)
    promotions = Promotion.objects.all().order_by('-id')

    return render(request, 'promotions.html', {
        'combined_values': combined_values,
        'promotions': promotions
    })


from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from .models import OrderGroup

@login_required
def track_order(request):
    order = None
    searched = False
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        try:
            order = OrderGroup.objects.get(id=order_id, user=request.user)
            searched = True
        except OrderGroup.DoesNotExist:
            messages.error(request, "❌ No order found with that ID.")
    return render(request, 'store/track_order.html', {
        'order': order,
        'searched': searched
    })
