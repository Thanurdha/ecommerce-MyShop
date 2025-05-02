# store/context_processors.py

from .models import CartItem

def cart_item_count(request):
    if request.user.is_authenticated:
        count = CartItem.objects.filter(user=request.user).count()
    else:
        count = 0
    return {'cart_item_count': count}


# store/context_processors.py

from .models import CartItem

def cart_item_count(request):
    if request.user.is_authenticated:
        count = sum(item.quantity for item in CartItem.objects.filter(user=request.user))
    else:
        count = 0
    return {'cart_item_count': count}
