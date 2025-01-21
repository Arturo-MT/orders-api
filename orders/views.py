from rest_framework import viewsets
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Order, OrderItem, Product, ProductCategory, Store
from .serializers import OrderSerializer, OrderItemSerializer, ProductSerializer, ProductCategorySerializer, StoreSerializer
from .utils.print_ticket import print_ticket
from django.views.generic import TemplateView
from django.utils.timezone import now
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import json


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'
    login_url = 'auth_login'

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
            messages.success(request, "Ticket impreso exitosamente.")
        else:
            raise Exception(f"Error al imprimir ticket: {response_text}")
        return redirect('home')


@method_decorator(login_required, name='dispatch')
class CategoryTemplateView(View):
    template_name = "categories.html"

    def get(self, request):
        categories = ProductCategory.objects.all()
        return render(request, self.template_name, {"categories": categories})

    def post(self, request):
        try:
            name = request.POST.get("name")
            store_id = request.POST.get("store")

            if ProductCategory.objects.filter(name=name, store_id=store_id).exists():
                raise ValueError(
                    "Ya existe una categoría con este nombre en la tienda.")

            if not name:
                raise ValueError("El nombre de la categoría es obligatorio.")

            ProductCategory.objects.create(name=name, store_id=store_id)
            messages.success(request, "Categoría creada exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al crear la categoría: {e}")
        return redirect("category_template_view")


@method_decorator(login_required, name='dispatch')
class ProductTemplateView(View):
    template_name = "products.html"

    def get(self, request):
        products = Product.objects.all()
        categories = ProductCategory.objects.all()
        return render(request, self.template_name, {"products": products, "categories": categories})

    def post(self, request):
        try:
            name = request.POST.get("name")
            category_id = request.POST.get("category")
            price = request.POST.get("price")
            store_id = request.POST.get("store")

            if not name or not category_id or not price:
                raise ValueError("Todos los campos son obligatorios.")

            Product.objects.create(
                name=name,
                category_id=category_id,
                price=price,
                store_id=store_id,
            )
            messages.success(request, "Producto creado exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al crear el producto: {e}")
        return redirect("product_template_view")


class CreateOrderTemplateView(View):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        order_data = request.POST.get('order_data')
        if not order_data:
            messages.error(request, "No se proporcionaron datos de la orden.")
            return redirect('home')

        try:
            data = json.loads(order_data)
        except json.JSONDecodeError:
            messages.error(
                request, "El formato de los datos de la orden no es válido.")
            return redirect('home')

        customer_name = data.get('customer_name')
        items = data.get('items', [])
        order_type = data.get('type')

        if not customer_name or not order_type or not items:
            messages.error(
                request, "Faltan campos requeridos (nombre del cliente, tipo de orden o productos).")
            return redirect('home')

        store_id = request.POST.get('store')
        if not store_id:
            messages.error(request, "Falta el ID de la tienda.")
            return redirect('home')

        store = get_object_or_404(Store, id=store_id)

        order = Order.objects.create(
            customer_name=customer_name,
            type=order_type,
            customer=request.user,
            store=store
        )

        for item in items:
            product_id = item.get('product')
            quantity = item.get('quantity')
            description = item.get('description')

            if not product_id or not quantity:
                messages.error(request, "Faltan datos de producto o cantidad.")
                return redirect('home')

            OrderItem.objects.create(
                order=order,
                product_id=product_id,
                quantity=quantity,
                description=description
            )

        serializer = OrderSerializer(order)

        print_ticket(order_id=order.id, request=request)

        messages.success(request, "La orden se ha creado con éxito.")

        return redirect('home')


# API Views


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
