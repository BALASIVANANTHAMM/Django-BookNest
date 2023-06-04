from django.urls import path
from . import views
from django.contrib.auth import views as auth_view
from .form import MyPasswordResetForm, MySetPasswordForm

urlpatterns = [
    path('', views.home, name="home"),
    path('register', views.register, name="register"),
    path('login', views.login_page, name="login"),
    path('logout', views.logout_page, name="logout"),
    path('cart', views.cart_page, name="cart"),
    path('profile', views.ProfileView.as_view(), name="profile"),
    path('address', views.address, name="address"),
    path('updateAddress/<int:pk>/', views.updateAddress.as_view(), name="updateAddress"),
    path('checkout', views.checkout.as_view(), name="checkout"),
    path('fav', views.fav_page, name="fav"),
    path('orders', views.orders.as_view(), name="orders"),
    path('paymentdone', views.payment_done, name="paymentdone"),
    path('favviewpage', views.favviewpage, name='favviewpage'),
    path('remove_cart/<str:cid>/', views.remove_cart, name="remove_cart"),
    path('remove_fav/<str:fid>/', views.remove_fav, name="remove_fav"),
    path('collections', views.collections, name="collections"),
    path('collections/<str:name>/', views.collectionsview, name="collections"),
    path('collections/<str:name>/<str:pname>/', views.product_details, name="product_details"),
    path('addtocart', views.add_to_cart, name="addtocart"),

    path('password-reset/',
         auth_view.PasswordResetView.as_view(template_name='webs/password_reset.html', form_class=MyPasswordResetForm),
         name='password_reset'),

    path('password-reset/done/',
         auth_view.PasswordResetDoneView.as_view(template_name='webs/password_reset_done.html'),
         name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/',
         auth_view.PasswordResetConfirmView.as_view(template_name='webs/password_reset_confirm.html',
                                                    form_class=MySetPasswordForm),
         name='password_reset_confirm'),

    path('password-reset-complete/',
         auth_view.PasswordResetCompleteView.as_view(template_name='webs/password_reset_complete.html',
                                                     ), name='password_reset_complete'),

]
