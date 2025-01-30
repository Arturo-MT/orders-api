from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from .models import Order


@receiver(post_save, sender=Order)
def set_order_number(sender, instance, created, **kwargs):
    if created and not instance.order_number:
        pk_str = str(instance.pk).zfill(3)
        instance.order_number = f'{now().strftime("%y%m%d")}-{pk_str}'
        instance.save(update_fields=['order_number'])
