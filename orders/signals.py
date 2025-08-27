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


@receiver(post_save, sender=Order)
def check_duplicate_order(sender, instance, created, **kwargs):
    if not created:
        return

    try:
        prev_number = str(
            int(instance.order_number.split("-")[-1]) - 1).zfill(3)
        prev_order_number = f"{instance.order_number.split('-')[0]}-{prev_number}"
        prev_order = Order.objects.prefetch_related("orderitem_set__product").get(
            order_number=prev_order_number
        )
    except Order.DoesNotExist:
        return

    new_signature = tuple(
        sorted(
            (item.product_id, item.quantity, float(item.price))
            for item in instance.orderitem_set.all()
        )
    )
    prev_signature = tuple(
        sorted(
            (item.product_id, item.quantity, float(item.price))
            for item in prev_order.orderitem_set.all()
        )
    )

    if (
        instance.customer_name == prev_order.customer_name
        and new_signature == prev_signature
    ):
        print(
            f"❌ Orden duplicada detectada: {instance.order_number}. Eliminando...")
        instance.delete()
