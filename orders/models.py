from django.db import models
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import os

class ProductCategory(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    #ToDo: Update category to an actual default category defined in the database
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, blank=True, null=True)
    
    def path_to_product(self, filename):
        return f'previews/temp/preview.jpg'

    preview = models.ImageField(upload_to=path_to_product, blank=True, null=True, verbose_name='preview')

    def __str__(self):
        return self.name

class Order(models.Model):
    TYPES = [('T', 'To go'), ('F', 'For here')]

    type = models.CharField(max_length=255, choices=TYPES, blank=False, null=False)
    customer = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, blank=True, null=True)
    order_number = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order {self.order_number}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=False, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=False, null=False)
    quantity = models.PositiveIntegerField(blank=False, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.quantity}x {self.product.name}'

@receiver(post_save, sender=Order)
def set_order_number(sender, instance, created, **kwargs):
    if created and not instance.order_number:
        pk_str = str(instance.pk).zfill(3)
        instance.order_number = f'{now().strftime("%y%m%d")}-{pk_str}'
        instance.save(update_fields=['order_number'])

@receiver(post_save, sender=Product)
def update_file_path(instance, created, **kwargs):
    if created and instance.preview and 'temp' in instance.preview.path:
        initial_path = instance.preview.path
        new_path = settings.MEDIA_ROOT + f'/previews/{instance.id}/preview.jpg'
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        os.rename(initial_path, new_path)
        instance.preview.name = f'previews/{instance.id}/preview.jpg'
        instance.save()
