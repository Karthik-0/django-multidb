from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^blogs/', include('blog.urls')),
    url(r'^', include('institutes.urls')),
]
