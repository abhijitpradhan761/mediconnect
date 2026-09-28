from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Notification


@method_decorator(login_required, name='dispatch')
class NotificationListView(View):
    """Lists all user notifications with read/unread status filters."""
    def get(self, request):
        user_notifications = Notification.objects.filter(recipient=request.user)
        unread_count = user_notifications.filter(is_read=False).count()
        return render(request, 'notifications/notification_list.html', {
            'notifications': user_notifications,
            'unread_count': unread_count,
        })


@method_decorator(login_required, name='dispatch')
class MarkNotificationReadView(View):
    """Marks a single notification as read."""
    def post(self, request, pk):
        notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notif.is_read = True
        notif.save()
        messages.success(request, "Notification marked as read.")
        return redirect('notifications_list')


@method_decorator(login_required, name='dispatch')
class MarkAllNotificationsReadView(View):
    """Marks all notifications for current user as read."""
    def post(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        messages.success(request, "All notifications marked as read.")
        return redirect('notifications_list')
