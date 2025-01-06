from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer

class LoginView(APIView):
    template_name = 'login.html'

    def get(self, request):
        return render(request, self.template_name)
    
    def form_invalid(self, form):
        return super().form_invalid(form)

    def post(self, request):
        email = request.data.get('email', None)
        password = request.data.get('password', None)
        user = authenticate(email=email, password=password)
    
        if user:
            login(request, user)
            #ToDo: Give a response when migrate to a separate frontend
            return redirect('/')
        
        return Response(status=status.HTTP_404_NOT_FOUND)

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        #ToDo: Give a response when migrate to a separate frontend
        return redirect('/')
    
class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    template_name = 'register.html'

    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            #ToDo: Give a response when migrate to a separate frontend
            return redirect('/')
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
