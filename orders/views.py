from rest_framework import viewsets
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views.generic import TemplateView
from .models import Order, OrderItem, Product, ProductCategory
from .serializers import OrderSerializer, OrderItemSerializer, ProductSerializer, ProductCategorySerializer

class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        context['categories'] = ProductCategory.objects.all()
        return context

class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    # ToDo: Add permission classes when open to public so only admin can create categories
    permission_classes = [IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # ToDo: Add permission classes when open to public so only admin can create products
    permission_classes = [IsAuthenticated]

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    # ToDo: Add permission classes when open to public so pubic can create order_items
    permission_classes = [IsAuthenticated]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # ToDo: Add permission classes when open to public so public can create orders
    permission_classes = [IsAuthenticated]

class CreateOrderView(APIView):
    # ToDo: Add permission classes when open to public so public can create orders
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        customer_id = data.get('customer')
        items = data.get('items', [])
        order_type = data.get('type')

        order = Order.objects.create(customer_id=customer_id, type=order_type)

        for item in items:
            product_id = item.get('product')
            quantity = item.get('quantity')
            OrderItem.objects.create(order=order, product_id=product_id, quantity=quantity)

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
