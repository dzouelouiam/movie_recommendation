from django.contrib import admin
from django.urls import path, include

    
urlpatterns = [
    path("admin/", admin.site.urls),
    #routing the user to go to the pages to match the root ( urls.py base)
    path('',include('base.urls')),
    path('api/',include('base.api.urls'))
]
