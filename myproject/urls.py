from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
    
urlpatterns = [
    path("admin/", admin.site.urls),
    #routing the user to go to the pages to match the root ( urls.py base)
    path('',include('base.urls')),
    path('api/',include('base.api.urls'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)