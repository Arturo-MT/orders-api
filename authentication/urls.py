from django.urls import path, include
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
]