from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .views import CurrentUserView

from .views import LoginView, LogoutView, RegisterView, SettingsTemplateView

urlpatterns = [
    path('login/',
         LoginView.as_view(), name='auth_login'),
    path('logout/',
         LogoutView.as_view(), name='auth_logout'),
    path('register/',
         RegisterView.as_view(), name='auth_register'),
    path('reset/',
         include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('settings/',
         SettingsTemplateView.as_view(), name='account_settings'),
    path('token/',
         TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/',
         TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/',
         TokenVerifyView.as_view(), name='token_verify'),
    path('me/',
         CurrentUserView.as_view(), name='user_me'),
]
