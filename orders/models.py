from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.db.models import Sum
from django.dispatch import receiver
from django.utils.timezone import now
from datetime import timedelta
from django.utils import timezone
from django.db.models.signals import pre_save
import os


class Store(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return self.name

    def get_orders_count(self, start_date=None, end_date=None):
        orders = Order.objects.filter(store=self)
        if start_date and end_date:
            orders = orders.filter(created_at__range=(start_date, end_date))
        return orders.count()

    def get_revenue(self, start_date=None, end_date=None):
        orders = Order.objects.filter(store=self)
        if start_date and end_date:
            orders = orders.filter(created_at__range=(start_date, end_date))
        return orders.aggregate(total_revenue=Sum('total'))['total_revenue'] or 0

    def get_stats(self):
        today = now().date()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)

        return {
            'orders_today': self.get_orders_count(start_date=today, end_date=today + timedelta(days=1)),
            'orders_this_week': self.get_orders_count(start_date=start_of_week, end_date=today + timedelta(days=1)),
            'orders_this_month': self.get_orders_count(start_date=start_of_month, end_date=today + timedelta(days=1)),
            'orders_this_year': self.get_orders_count(start_date=start_of_year, end_date=today + timedelta(days=1)),
            'revenue_today': self.get_revenue(start_date=today, end_date=today + timedelta(days=1)),
            'revenue_this_week': self.get_revenue(start_date=start_of_week, end_date=today + timedelta(days=1)),
            'revenue_this_month': self.get_revenue(start_date=start_of_month, end_date=today + timedelta(days=1)),
            'revenue_this_year': self.get_revenue(start_date=start_of_year, end_date=today + timedelta(days=1)),
        }


class ProductCategory(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, blank=False, null=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # ToDo: Update category to an actual default category defined in the database
    category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, blank=True, null=True)

    def path_to_product(self, filename):
        return f'previews/temp/preview.jpg'

    preview = models.ImageField(
        upload_to=path_to_product, blank=True, null=True, verbose_name='preview')

    def __str__(self):
        return self.name


class Order(models.Model):
    TYPES = [('T', 'To go'), ('F', 'For here')]
    STATUS_CHOICES = [
        ('P', 'Pendiente'),
        ('C', 'Completada'),
        ('X', 'Cancelada'),
    ]

    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, blank=False, null=False)
    type = models.CharField(
        max_length=255, choices=TYPES, blank=False, null=False)
    customer = models.ForeignKey(
        'authentication.CustomUser', on_delete=models.CASCADE, blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='P')
    order_number = models.CharField(
        max_length=20, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order {self.order_number}'

    @property
    def total(self):
        return sum(item.price for item in self.orderitem_set.all())


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, blank=False, null=False)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=False, null=False)
    quantity = models.PositiveIntegerField(blank=False, null=False)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.quantity}x {self.product.name}'


@receiver(post_save, sender=Product)
def update_file_path(instance, created, **kwargs):
    if created and instance.preview and 'temp' in instance.preview.path:
        initial_path = instance.preview.path
        new_path = settings.MEDIA_ROOT + f'/previews/{instance.id}/preview.jpg'
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        os.rename(initial_path, new_path)
        instance.preview.name = f'previews/{instance.id}/preview.jpg'
        instance.save()


@receiver(pre_save, sender=Order)
def set_order_number(sender, instance, **kwargs):
    if not instance.order_number:
        today = timezone.localtime().date()
        date_str = today.strftime('%y%m%d')
        count_today = Order.objects.filter(created_at__date=today).count() + 1
        instance.order_number = f'{date_str}-{count_today:03}'
