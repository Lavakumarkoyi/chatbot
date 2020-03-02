from django.conf.urls import url
from .bots import *
from .groups import *
from .intents import *

urlpatterns = [
    url('bot-form/', create_bot_form.as_view()),
    url('bots/', create_bot.as_view()),
    url('groups/', create_group.as_view(), name='create_group'),
    url('group-form/', create_group_form.as_view(), name="group_form"),
    url('intent-form/', create_intent_form.as_view(), name='create_intent_form'),
    url('intents/', create_intent.as_view(), name="create_intent"),
]
