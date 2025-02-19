from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from .models import Product, Order, OrderItem, ProductCategory, Store
from django.core.files.uploadedfile import SimpleUploadedFile


class OrderModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_model = get_user_model()
        cls.store = Store.objects.create(name="Test Store")

        cls.user, created = cls.user_model.objects.get_or_create(
            email='testuser11@example.com',
            defaults={
                "password": "password123",
                "first_name": "Test",
                "last_name": "User",
                "username": "testuser11",
                "phone_number": "1234567890",
                "store": cls.store,
            }
        )
        if created:
            cls.user.set_password("password123")
            cls.user.save()

        cls.category = ProductCategory.objects.create(name='Test Category', store=cls.store)

        cls.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=10.00,
            category=cls.category,
            preview=SimpleUploadedFile('test.jpg', b'file_content', content_type='image/jpeg'),
            store=cls.store,
        )

        cls.order = Order.objects.create(type='T', customer=cls.user, store=cls.store)

        cls.order_item = OrderItem.objects.create(
            order=cls.order,
            product=cls.product,
            quantity=2
        )

    def test_order_creation(self):
        self.assertEqual(self.order.type, 'T')
        self.assertEqual(self.order.customer, self.user)
        self.assertIsNotNone(self.order.order_number)
        self.assertTrue(self.order.order_number.startswith(now().strftime("%y%m%d")))
        self.assertTrue(self.order.order_number.endswith(f'{str(self.order.pk).zfill(3)}'))

    def test_order_str(self):
        self.assertEqual(str(self.order), f'Order {self.order.order_number}')

    def test_order_item_creation(self):
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product, self.product)
        self.assertEqual(self.order_item.quantity, 2)
        self.assertEqual(self.order_item.price, self.product.price * self.order_item.quantity)

    def test_order_item_str(self):
        self.assertEqual(str(self.order_item), f'2x {self.product.name}')

    def test_product_path(self):
        expected_path = f'/code/app/media/previews/{self.product.id}/preview.jpg'
        self.assertEqual(self.product.preview.path, expected_path)
