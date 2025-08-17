from rest_framework import viewsets
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from .models import Order, OrderItem, Product, ProductCategory, Store
from .serializers import OrderSerializer, OrderItemSerializer, ProductSerializer, ProductCategorySerializer, StoreSerializer
from .utils.print_ticket import print_ticket
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
from datetime import timedelta, datetime
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


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    login_url = 'auth_login'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store = self.request.user.store

        selected_period = self.request.GET.get('period', 'today')

        today = timezone.localtime(timezone.now()).date()
        start_of_day = timezone.make_aware(
            datetime.combine(today, datetime.min.time()))
        start_of_week = start_of_day - timedelta(days=start_of_day.weekday())
        start_of_month = start_of_day.replace(day=1)
        start_of_year = start_of_day.replace(month=1, day=1)

        orders = Order.objects.filter(store=store).order_by('-created_at')
        total_orders = orders.count()
        total_revenue = sum(order.total for order in orders)

        orders_today = Order.objects.filter(
            store=store, created_at__date=start_of_day)
        orders_week = Order.objects.filter(
            store=store, created_at__gte=start_of_week)
        orders_month = Order.objects.filter(
            store=store, created_at__gte=start_of_month)
        orders_year = Order.objects.filter(
            store=store, created_at__gte=start_of_year)

        total_orders_today = orders_today.count()
        total_orders_week = orders_week.count()
        total_orders_month = orders_month.count()
        total_orders_year = orders_year.count()

        total_revenue_today = sum(order.total for order in orders_today)
        total_revenue_week = sum(order.total for order in orders_week)
        total_revenue_month = sum(order.total for order in orders_month)
        total_revenue_year = sum(order.total for order in orders_year)

        if selected_period == 'today':
            orders = orders.filter(created_at__date=start_of_day)
            total_orders = total_orders_today
            total_revenue = total_revenue_today
        elif selected_period == 'week':
            orders = orders.filter(created_at__gte=start_of_week)
            total_orders = total_orders_week
            total_revenue = total_revenue_week
        elif selected_period == 'month':
            orders = orders.filter(created_at__gte=start_of_month)
            total_orders = total_orders_month
            total_revenue = total_revenue_month
        elif selected_period == 'year':
            orders = orders.filter(created_at__gte=start_of_year)
            total_orders = total_orders_year
            total_revenue = total_revenue_year

        page = self.request.GET.get('page')
        paginator = Paginator(orders, self.paginate_by)

        try:
            orders_page = paginator.page(page)
        except PageNotAnInteger:
            orders_page = paginator.page(1)
        except EmptyPage:
            orders_page = paginator.page(paginator.num_pages)

        context.update({
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'orders_page': orders_page,
            'selected_period': selected_period,
        })

        return context


class PrintTicketView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order_id = request.POST.get("order_id")
        print_ticket(order_id=order_id, request=request)

        return redirect(request.META.get("HTTP_REFERER", "home"))


class CategoryTemplateView(LoginRequiredMixin, View):
    template_name = "categories.html"
    login_url = 'auth_login'

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


class ProductTemplateView(LoginRequiredMixin, View):
    template_name = "products.html"
    login_url = 'auth_login'

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
            store=store,
        )

        for item in items:
            product_id = item.get('product')
            quantity = item.get('quantity')
            description = item.get('description')
            price = item.get('price')

            if not product_id or not quantity:
                messages.error(request, "Faltan datos de producto o cantidad.")
                return redirect('home')

            OrderItem.objects.create(
                order=order,
                product_id=product_id,
                quantity=quantity,
                price=price,
                description=description
            )

        print_ticket(order_id=order.id, request=request)

        messages.success(request, "La orden se ha creado con éxito.")

        return redirect('home')


# API Views


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProductCategory.objects.filter(store=self.request.user.store).order_by('name')


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(store=self.request.user.store).order_by('name')


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderItem.objects.filter(order__store=self.request.user.store)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(store=self.request.user.store)


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Store.objects.all()


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        customer_name = data.get('customer_name')
        items = data.get('items', [])
        order_type = data.get('type')
        order_status = data.get('status', 'P')

        if not customer_name or not order_type or not items:
            return Response({"error": "Faltan datos obligatorios"}, status=status.HTTP_400_BAD_REQUEST)

        store = get_object_or_404(Store, id=request.data.get('store'))

        order = Order.objects.create(
            customer_name=customer_name,
            type=order_type,
            customer=request.user,
            store=store,
            status=order_status
        )

        for item in items:
            product_id = item.get('product')
            quantity = item.get('quantity')
            description = item.get('description')
            price = item.get('price')

            if not product_id or not quantity:
                return Response({"error": "Datos de producto incompletos"}, status=status.HTTP_400_BAD_REQUEST)

            OrderItem.objects.create(
                order=order,
                product_id=product_id,
                quantity=quantity,
                price=price,
                description=description
            )

        order = (
            Order.objects
            .prefetch_related('orderitem_set__product')
            .get(pk=order.pk)
        )

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        store = request.user.store

        today = timezone.localtime(timezone.now()).date()
        start_of_day = timezone.make_aware(
            datetime.combine(today, datetime.min.time()))
        start_of_week = start_of_day - timedelta(days=start_of_day.weekday())
        start_of_month = start_of_day.replace(day=1)
        start_of_year = start_of_day.replace(month=1, day=1)

        all_orders = Order.objects.filter(store=store).order_by('-created_at')

        def calculate_summary(queryset):
            return {
                "total_orders": queryset.count(),
                "total_revenue": sum(order.total for order in queryset)
            }

        summary = {
            "today": calculate_summary(all_orders.filter(created_at__date=start_of_day)),
            "week": calculate_summary(all_orders.filter(created_at__gte=start_of_week)),
            "month": calculate_summary(all_orders.filter(created_at__gte=start_of_month)),
            "year": calculate_summary(all_orders.filter(created_at__gte=start_of_year)),
            "all": calculate_summary(all_orders)
        }

        filtered_orders = all_orders
        search = request.GET.get('search', '').strip()
        if search:
            filtered_orders = filtered_orders.filter(
                customer_name__icontains=search)

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_orders = paginator.paginate_queryset(
            filtered_orders, request)

        orders_data = [
            {
                "id": o.id,
                "customer_name": o.customer_name,
                "order_number": o.order_number,
                "total": o.total,
                "created_at": o.created_at,
                "status": o.status,
            }
            for o in paginated_orders
        ]

        return paginator.get_paginated_response({
            "summary": summary,
            "orders": orders_data
        })
