from rest_framework import serializers
from .models import Order, OrderItem, Product, ProductCategory, Store


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all())

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category', 'preview', 'store']


class OrderItemSerializer(serializers.ModelSerializer):
    class NestedProductSerializer(serializers.ModelSerializer):
        class Meta:
            model = Product
            fields = ['id', 'name', 'price']

    product = NestedProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price', 'description']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'customer_name', 'order_number',
                  'type', 'created_at', 'updated_at', 'items']
