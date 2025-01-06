from django.core.management.base import BaseCommand
from orders.models import Order, OrderItem, Product, ProductCategory

class Command(BaseCommand):
    help = 'Clears all data from the database'

    def handle(self, *args, **options):
        Order.objects.all().delete()
        OrderItem.objects.all().delete()
        Product.objects.all().delete()
        ProductCategory.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Data cleared successfully'))
