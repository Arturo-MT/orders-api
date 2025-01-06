from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from orders.views import ProductCategoryViewSet, ProductViewSet, OrderItemViewSet, OrderViewSet, CreateOrderView, HomePageView
from rest_framework import routers

router = routers.DefaultRouter()

# Orders app views
router.register(r'product-categories', ProductCategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('authentication.urls')),
    path('api/create-order/', CreateOrderView.as_view(), name='create-order'),
]

if settings.DEBUG:
    urlpatterns += static('/media/', document_root=settings.MEDIA_ROOT)
