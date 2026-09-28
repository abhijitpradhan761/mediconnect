from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListAPIView(APIView):
    """
    GET /api/notifications/ - list notifications
    POST /api/notifications/ - mark all read
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(recipient=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    def post(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'message': 'All notifications marked as read.'})


class NotificationDetailAPIView(APIView):
    """
    PATCH /api/notifications/<pk>/ - toggle read state
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notif.is_read = request.data.get('is_read', True)
        notif.save()
        return Response(NotificationSerializer(notif).data)


class UnreadNotificationCountAPIView(APIView):
    """
    GET /api/notifications/unread-count/ - returns unread count for navbar badge
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'unread_count': count})
