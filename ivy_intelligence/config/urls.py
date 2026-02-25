from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('apps.opportunities.urls')),
    path('profiles/', include('apps.profiles.urls')),
    path('applications/', include('apps.applications.urls')),
    path('community/', include('apps.community.urls')),
    path('incoscore/', include('apps.incoscore.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customisation
admin.site.site_header = "Ivy Intelligence Admin"
admin.site.site_title = "Ivy Intelligence"
admin.site.index_title = "Platform Administration"
