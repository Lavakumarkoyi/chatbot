from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Menu(models.Model):
    MenuName = models.CharField(max_length=20, primary_key=True)
    MenuIcon = models.CharField(max_length=20)
    userAccess = models.CharField(max_length=255, null=True, blank=True)


class SubMenu(models.Model):
    Menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    SubMenuName = models.CharField(max_length=20)
    Link = models.CharField(max_length=255)

# clientadmin and user relationship Model


class client(models.Model):
    client_name = models.CharField(max_length=50, unique=True)
    client_logo = models.URLField(max_length=255, null=True, blank=True)
    client_added = models.DateTimeField(auto_now=True)


class client_user(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    client_id = models.ForeignKey(client, on_delete=models.CASCADE)
