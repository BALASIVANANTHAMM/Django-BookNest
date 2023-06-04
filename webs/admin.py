from django.contrib import admin
from .models import *

admin.site.register(Catagory)
admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(OrderPlace)
admin.site.register(Payment)