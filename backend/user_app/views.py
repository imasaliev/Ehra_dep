from django.shortcuts import render, get_list_or_404, get_object_or_404
from .models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)
from django.http import HttpResponse
from .serializers import UserOnlySerializer, UserSerializer
from django.contrib.auth.hashers import make_password


# Create your views here.


class User_permissions(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class Log_in(APIView):
    def post(self, request):
        request.data["username"] = request.data["email"]
        user = authenticate(**request.data)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"user": UserSerializer(user).data, "token": token.key})
        else:
            return Response("Something went wrong", status=HTTP_400_BAD_REQUEST)


class Sign_up(APIView):
    def post(self, request):
        request.data["username"] = request.data["email"]
        user = User.objects.create_user(**request.data)
        token = Token.objects.create(user=user)
        return Response(
            {"user": UserSerializer(user).data, "token": token.key}, status=HTTP_201_CREATED
        )


class Info(User_permissions):
    def get(self, request):
        user = get_object_or_404(User, email=request.user.email)
        return Response(UserSerializer(user).data)

    def put(self, request):
        user = get_object_or_404(User, email=request.user.email)
        User.objects.filter(id=user.id).update(**request.data)
        user.password = make_password(request.data.get("password"))
        user.first_name = request.data.get("first_name")
        user.last_name = request.data.get("last_name")
        user.email = request.data.get("email")
        user.username = request.data.get("email")
        user.save()

        return Response(UserSerializer(user).data)

    def delete(self, request):
        user = get_object_or_404(User, email=request.user.email)
        User.objects.filter(id=user.id).delete()
        return Response(status=HTTP_204_NO_CONTENT)


class Log_out(User_permissions):
    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=HTTP_204_NO_CONTENT)
