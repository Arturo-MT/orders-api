from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.db import IntegrityError
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
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
