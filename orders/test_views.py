from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Product, ProductCategory, Order, OrderItem
from .serializers import ProductSerializer, ProductCategorySerializer
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.test import APIClient


class ProductCategoryViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = ProductCategory.objects.create(name='Drinks')
        self.url = reverse('productcategory-list')

    def test_create_product_category(self):
        data = {'name': 'Food'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductCategory.objects.count(), 2)
        self.assertEqual(ProductCategory.objects.get(id=response.data['id']).name, 'Food')

class ProductViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = ProductCategory.objects.create(name='Drinks')
        self.product = Product.objects.create(name='Soda', category=self.category, price=10.00)
        self.url = reverse('product-list')

    def test_get_products(self):
        response = self.client.get(self.url)
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_product(self):
        data = {
            'name': 'Soda',
            'category': self.category.id,
            'price': 500.00,
            'description': 'This is a test product'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(Product.objects.get(id=response.data['id']).name, 'Soda')

class OrderViewTestCase(APITestCase):
    def setUp(self):
        Product.objects.all().delete()
        self.user_model = get_user_model()
        self.category = ProductCategory.objects.create(name='Test Category')
        self.superuser = self.user_model.objects.create_superuser(
            email='superuser1@example.com',
            username='superuser1',
            first_name='John',
            last_name='Doe',
            phone_number='1234467899',
            password='superuserpassword',
        )
        self.product1 = Product.objects.create(
            name='Test Product 1',
            price=10.99,
            description='This is a test product 1',
            category=self.category
        )
        self.product2 = Product.objects.create(
            name='Test Product 2',
            price=10.99,
            description='This is a test product 2',
            category=self.category
        )
    
    def test_create_order(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(
            reverse('create-order'),
            {
                'customer': self.superuser.id,
                'items': [
                    {
                        'product': self.product1.id,
                        'quantity': 2
                    },
                    {
                        'product': self.product2.id,
                        'quantity': 1
                    }
                ],
                'type': 'T' # To go
            },
            format='json'
        )
        order = Order.objects.get()
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 2)
        self.assertEqual(order.type, 'T')
