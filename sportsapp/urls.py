from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('sports.urls')),
]
handler404 = 'sports.views.custom_404_view'
handler500 = 'sports.views.custom_500_view'
