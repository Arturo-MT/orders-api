from rest_framework import viewsets
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views.generic import TemplateView
from .models import Order, OrderItem, Product, ProductCategory, Store
from .serializers import OrderSerializer, OrderItemSerializer, ProductSerializer, ProductCategorySerializer, StoreSerializer
import json
from .utils.print_ticket import print_ticket
from django.utils.timezone import now


class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(
            store=self.request.user.store)
        context['categories'] = ProductCategory.objects.filter(
            store=self.request.user.store)
        return context


class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store = self.request.user.store
        orders = Order.objects.filter(store=store).order_by('-created_at')
        context['orders'] = orders
        context['total_orders'] = orders.count()
        context['total_sales'] = sum(order.total for order in orders)
        context['today_sales'] = sum(
            order.total for order in orders.filter(created_at__date=now().date()))
        context['today_orders'] = orders.filter(
            created_at__date=now().date()).count()
        return context


class PrintTicketView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        status_code, response_text = print_ticket(
            order_id=request.data.get('order_id'))
        if status_code == 200:
            return Response({"message": "Ticket impreso correctamente"}, status=status_code)
        else:
            return Response({"error": response_text}, status=status_code)


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


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    # ToDo: Add permission classes when open to public so store can be created
    permission_classes = [IsAuthenticated]


class CreateOrderView(APIView):
    # ToDo: Add permission classes when open to public so public can create orders
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        order_data = request.POST.get('order_data')
        data = json.loads(order_data)
        customer_name = data.get('customer_name')
        items = data.get('items', [])
        order_type = data.get('type')
        customer = request.user
        store_id = request.POST.get('store')

        store = Store.objects.get(id=store_id)

        order = Order.objects.create(
            customer_name=customer_name, type=order_type, customer=customer, store=store)

        for item in items:
            product_id = item.get('product')
            quantity = item.get('quantity')
            description = item.get('description')
            OrderItem.objects.create(
                order=order, product_id=product_id, quantity=quantity, description=description)

        serializer = OrderSerializer(order)
        print_ticket(order_id=order.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
