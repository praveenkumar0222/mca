from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import dashboard 



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='home'),  # Add this line for root URL
    path('accounts/', include('accounts.urls')),
    path('exams/', include('exams.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('accounts.urls')),
#     path('exams/', include('exams.urls')),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)