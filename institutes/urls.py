from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^hello/$', views.hello_view, name='hello'),
]
