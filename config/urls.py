"""
URL configuration for MediConnect project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import home_view

urlpatterns = [
    # System Administration
    path('admin/', admin.site.urls),

    # Public Landing Page
    path('', home_view, name='home'),

    # Accounts & Authentication (Login, Register, Logout, Redirects)
    path('accounts/', include('accounts.urls')),
]

# Serve media and static files during local development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
