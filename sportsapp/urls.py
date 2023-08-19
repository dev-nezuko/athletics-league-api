from django.contrib import admin
from django.conf.urls import handler404, handler500
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('sports.urls')),
]
handler404 = 'sports.views.custom_404_view'
handler500 = 'sports.views.custom_500_view'
