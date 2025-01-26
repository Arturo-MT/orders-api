from django.contrib import admin

from authentication.models import AccountSettings
from orders.models import Order, OrderItem, Product, ProductCategory, Store

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(Store)
admin.site.register(AccountSettings)
