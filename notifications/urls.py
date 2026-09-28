from django.urls import path
from . import views

urlpatterns = [
    # Web views
    path('', views.NotificationListView.as_view(), name='notifications_list'),
    path('<int:pk>/read/', views.MarkNotificationReadView.as_view(), name='mark_notification_read'),
    path('mark-all-read/', views.MarkAllNotificationsReadView.as_view(), name='mark_all_notifications_read'),
]
