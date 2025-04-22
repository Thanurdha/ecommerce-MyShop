from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('orders/', views.order_history, name='order_history'),
    path('about/', views.about, name='about'),
    path('category/<int:category_id>/', views.category_products, name='category_products'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('payment/', views.payment_page, name='payment'),
    path('todays-deals/', views.todays_deals, name='todays_deals'),
    path('search/', views.search_products, name='search'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

]
