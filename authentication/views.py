from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.views import View
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import AccountSettings
from .serializers import UserSerializer
from orders.models import Store


class LoginView(APIView):
    template_name = 'login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.data.get('email', None)
        password = request.data.get('password', None)
        user = authenticate(email=email, password=password)

        if user:
            login(request, user)
            return redirect('/')

        messages.error(
            request, 'Credenciales inválidas. Por favor, intenta de nuevo.')
        return render(request, self.template_name, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        messages.info(request, 'Has cerrado sesión exitosamente.')
        return redirect('/')


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    template_name = 'register.html'

    def get(self, request):
        stores = Store.objects.all()
        return render(request, self.template_name, {'stores': stores})

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.validated_data['password'] = make_password(
                serializer.validated_data['password']
            )
            try:
                serializer.save()
                messages.success(
                    request, 'Tu cuenta ha sido creada exitosamente.'
                )
                return redirect('/')
            except IntegrityError as e:
                messages.error(
                    request, 'Hubo un error al crear tu cuenta. Intenta nuevamente.')
                return redirect('auth_register')

        for field, error_list in serializer.errors.items():
            for error in error_list:
                messages.error(request, f"{field.capitalize()}: {error}")

        return redirect('auth_register')


class SettingsTemplateView(View):
    template_name = 'settings.html'
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        settings = AccountSettings.objects.filter(user=request.user)
        return render(request, self.template_name, {'settings': settings})

    def post(self, request):
        try:
            addr = request.POST.get("addr")
            if not addr:
                raise ValueError("La dirección IP es obligatoria.")
            settings, created = AccountSettings.objects.get_or_create(
                user=request.user,
                defaults={'addr': addr}
            )
            if not created:
                settings.addr = addr
                settings.save()
            messages.success(
                request, "La dirección IP se ha guardado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al guardar la dirección IP: {e}")
        return redirect("account_settings")


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
