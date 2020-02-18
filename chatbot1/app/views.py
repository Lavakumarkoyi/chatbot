from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from django.shortcuts import render
from rest_framework import status
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from django.views.generic import View


@login_required
def ChatView(request, username, bot_id):
    if request.user.username == username:
        return render(request, 'sadmin/chatapp.html')
