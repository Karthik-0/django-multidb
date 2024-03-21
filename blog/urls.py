from django.conf.urls import url
from .views import blog_list

urlpatterns = [
    url(r'', blog_list, name='blog_list'),
]
