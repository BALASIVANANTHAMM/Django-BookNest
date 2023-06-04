import razorpay
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from django.conf import settings

from .form import CustomUserForm, CustomerProfileForm
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import json


def home(request):
    products = Product.objects.filter(trending=1)
    return render(request, "webs/index.html", {"products": products})


def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Logged Out Successfully")
    return redirect("/")


def favviewpage(request):
    if request.user.is_authenticated:
        fav = Favourite.objects.filter(user=request.user)
        return render(request, "webs/fav.html", {"fav": fav})
    else:
        return redirect("/")


def remove_fav(request, fid):
    item = Favourite.objects.get(id=fid)
    item.delete()
    return redirect("/favviewpage")


def cart_page(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        return render(request, "webs/cart.html", {"cart": cart})
    else:
        return redirect("/")


def remove_cart(request, cid):
    cartitem = Cart.objects.get(id=cid)
    cartitem.delete()
    return redirect("/cart")


def add_to_cart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            data = json.load(request)
            product_qty = data['product_qty']
            product_id = data['pid']
            # print(request.user.id)
            product_status = Product.objects.get(id=product_id)
            if product_status:
                if Cart.objects.filter(user=request.user.id, product_id=product_id):
                    return JsonResponse({'status': 'Product Already in Cart'}, status=200)
                else:
                    if product_status.quantity >= product_qty:
                        Cart.objects.create(user=request.user, product_id=product_id, product_qty=product_qty)
                        return JsonResponse({'status': 'Product Added to Cart'}, status=200)
                    else:
                        return JsonResponse({'status': 'Product Stock Not Available'}, status=200)
        else:
            return JsonResponse({'status': 'Login to Add Cart'}, status=200)
    else:
        return JsonResponse({'status': 'Invalid Access'}, status=200)


class checkout(View):
    def get(self, request):
        user = request.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)
        famount = 0
        for p in cart_items:
            value = p.product_qty * p.product.selling_price
            famount = famount + value
        totalamount = famount + 40
        razoramount = int(totalamount * 100)
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        data = {"amount": razoramount, "currency": "INR", "receipt": "order_rcptid_12"}
        payment_response = client.order.create(data=data)
        print(payment_response)
        # {'id': 'order_Le1FffKvijb2uG', 'entity': 'order', 'amount': 75600, 'amo
        #     unt_paid': 0, 'amount_due': 75600, 'currency': 'INR', 'receipt': 'order
        #  _rcptid_12', 'offer_id': None, 'status': 'created', 'attempts': 0, 'notes': [], 'created_at': 1681551233}
        order_id = payment_response['id']
        order_status = payment_response['status']
        if order_status == 'created':
            payment = Payment(
                user=user,
                amount=totalamount,
                razorpay_order_id=order_id,
                razorpay_payment_status=order_status
            )
            payment.save()
        return render(request, "webs/checkout.html", locals())


def payment_done(request):
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    cust_id = request.GET.get('cust_id')
    # print("payment_done : oid = ",order_id," pid = " ', payment_id," cid = ",cust_id)
    user = request.user
    # return redirect("orders")
    customer = Customer.objects.get(id=cust_id)
    # To update payment status and payment id
    payment = Payment.objects.get(razorpay_order_id=order_id)
    payment.paid = True
    payment.razorpay_payment_id = payment_id
    payment.save()
    # To save order details
    cart = Cart.objects.filter(user=request.user)
    for c in cart:
        OrderPlace(user=user, customer=customer, product=c.product, product_qty=c.product_qty, payment=payment).save()
        c.delete()
    return redirect("orders")


class orders(View):
    def get(self, request):
        order_placed = OrderPlace.objects.filter(user=request.user)
        return render(request, 'webs/orders.html', locals())


def fav_page(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            data = json.load(request)
            product_id = data['pid']
            product_status = Product.objects.get(id=product_id)
            if product_status:
                if Favourite.objects.filter(user=request.user.id, product_id=product_id):
                    return JsonResponse({'status': 'Product Already in Favourite'}, status=200)
                else:
                    Favourite.objects.create(user=request.user, product_id=product_id)
                    return JsonResponse({'status': 'Product Added to Favourite'}, status=200)
        else:
            return JsonResponse({'status': 'Login to Add Favourite'}, status=200)
    else:
        return JsonResponse({'status': 'Invalid Access'}, status=200)


def login_page(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == 'POST':
            name = request.POST.get('username')
            pwd = request.POST.get('password')
            user = authenticate(request, username=name, password=pwd)
            if user is not None:
                login(request, user)
                messages.success(request, "Logged in Successfully")
                return redirect("/")
            else:
                messages.error(request, "Invalid User Name or Password")
                return redirect("/login")
        return render(request, "webs/login.html")


def register(request):
    form = CustomUserForm()
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration Successfully You Can Login Now...!")
            return redirect('/login')
    return render(request, "webs/register.html", {'form': form})


def collections(request):
    catagory = Catagory.objects.filter(status=0)
    return render(request, "webs/collections.html", {"catagory": catagory})


def collectionsview(request, name):
    if Catagory.objects.filter(name=name, status=0):
        products = Product.objects.filter(category__name=name)
        return render(request, "webs/products/index.html", {"products": products, "category_name": name})
    else:
        messages.warning(request, "No Such Category Found")
        return redirect('collection')


def product_details(request, name, pname):
    if Catagory.objects.filter(name=name, status=0):
        if Product.objects.filter(name=pname, status=0):
            products = Product.objects.filter(name=pname, status=0).first()
            return render(request, "webs/products/product_details.html", {"products": products})
        else:
            messages.error(request, "No Such Products Found")
            return redirect('collection')
    else:
        messages.error(request, "No Such Category Found")
        return redirect('collection')


class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'webs/profile.html', locals())

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            reg = Customer(user=user, name=name, locality=locality, city=city, mobile=mobile, state=state,
                           zipcode=zipcode)
            reg.save()
            messages.success(request, "Profile Saved Successfully")
        else:
            messages.warning(request, "Data Invalid")

        return render(request, 'webs/profile.html', locals())


def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'webs/address.html', locals())


class updateAddress(View):
    def get(self, request, pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request, 'webs/updateAddress.html', locals())

    def post(self, request, pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request, "Profile Updated Successfully")
        else:
            messages.warning(request, "Data Invalid")

        return redirect('address')
