from django.conf.urls import url
from .views import *

urlpatterns = [
    url('intent-form/', create_intent_form.as_view(), name='create_intent_form'),
    # url('responseform/', IntentResponseView.as_view()),
    url('create-intent', create_intent.as_view(), name="create_intent"),
]
