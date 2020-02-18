from django.conf.urls import url
from .views import *

urlpatterns = [
    url('createbot/', create_bot_form.as_view()),
    url('', create_bot.as_view()),

]
