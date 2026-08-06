from django.contrib import admin
from django.urls import include, path
from api.views import shared_estimate_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('share/<str:token>/', shared_estimate_view, name='shared-estimate'),
]
