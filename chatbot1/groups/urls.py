from django.conf.urls import url
from .views import *

urlpatterns = [
    url('create-group', create_group.as_view(), name='create_group'),
    url('group-form', create_group_form.as_view(), name="group_form"),
    # url('intent-flow', intent_flow.as_view(), name="intent_flow"),
]
