from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Product, ProductCategory, Order, Store
from .serializers import ProductSerializer, ProductCategorySerializer

User = get_user_model()

class ProductCategoryViewSetTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.store = Store.objects.create(name='Test Store')
        cls.category = ProductCategory.objects.create(name='Drinks', store=cls.store)
        cls.url = reverse('productcategory-list')
        cls.superuser = User.objects.create_superuser(
            email='superuser1@example.com',
            username='superuser1',
            first_name='John',
            last_name='Doe',
            phone_number='1234467899',
            password='superuserpassword',
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.superuser)

    def test_create_product_category(self):
        data = {'name': 'Food', 'store': self.store.id}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductCategory.objects.count(), 2)
        self.assertEqual(ProductCategory.objects.get(id=response.data['id']).name, 'Food')


class ProductViewSetTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.store = Store.objects.create(name='Test Store')
        cls.category = ProductCategory.objects.create(name='Drinks', store=cls.store)
        cls.product = Product.objects.create(name='Soda', category=cls.category, price=10.00, store=cls.store)
        cls.url = reverse('product-list')
        cls.superuser = User.objects.create_superuser(
            email='superuser1@example.com',
            username='superuser1',
            first_name='John',
            last_name='Doe',
            phone_number='1234467899',
            password='superuserpassword',
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.superuser)

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
            'description': 'This is a test product',
            'store': self.store.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(Product.objects.get(id=response.data['id']).name, 'Soda')


class OrderViewTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        Product.objects.all().delete()
        cls.store = Store.objects.create(name='Test Store')
        cls.category = ProductCategory.objects.create(name='Test Category', store=cls.store)
        cls.superuser = User.objects.create_superuser(
            email='superuser1@example.com',
            username='superuser1',
            first_name='John',
            last_name='Doe',
            phone_number='1234467899',
            password='superuserpassword',
        )
        cls.product1 = Product.objects.create(
            name='Test Product 1',
            price=10.99,
            description='This is a test product 1',
            category=cls.category,
            store=cls.store,
        )
        cls.product2 = Product.objects.create(
            name='Test Product 2',
            price=10.99,
            description='This is a test product 2',
            category=cls.category,
            store=cls.store,
        )
