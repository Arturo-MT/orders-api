from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from .models import Product, Order, OrderItem, ProductCategory
from django.core.files.uploadedfile import SimpleUploadedFile

class OrderModelTest(TestCase):

    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            email='testuser@example.com',
            password='password123',
            first_name='Test',
            last_name='User',
            username='testuser',
            phone_number='1234567890'
        )
        self.category = ProductCategory.objects.create(
            name='Test Category'
        )
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=10.00,
            category=self.category,
            preview=SimpleUploadedFile('test.jpg', b'file_content', content_type='image/jpeg')
        )
        self.order = Order.objects.create(
            type='T',
            customer=self.user
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
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
        self.assertEqual(self.product.preview.path, f'/code/media/previews/{self.product.id}/preview.jpg')
