from django.contrib import admin
from orders.models import Order, OrderItem, Product, ProductCategory

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Product)
admin.site.register(ProductCategory)
