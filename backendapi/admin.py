from django.contrib import admin
from .models import Category, Product, Order, SubCategory, Address, Payment, CustomUser, OrderItem

# Register your models here.
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(CustomUser)
admin.site.register(OrderItem)
admin.site.register(Product)
admin.site.register(Payment)
admin.site.register(Address)
admin.site.register(Order)
