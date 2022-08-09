from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import SessionAuthentication

from chat import settings
from core.serializers import MessageModelSerializer, UserModelSerializer
from core.models import MessageModel


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication scheme used by DRF. DRF's SessionAuthentication uses
    Django's session framework for authentication which requires CSRF to be
    checked. In this case we are going to disable CSRF tokens for the API.
    """

    def enforce_csrf(self, request):
        return


class MessagePagination(PageNumberPagination):
    """
    Limit message prefetch to one page.
    """

    page_size = settings.MESSAGES_TO_LOAD


class MessageModelViewSet(ModelViewSet):
    queryset = MessageModel.objects.all()
    serializer_class = MessageModelSerializer
    allowed_methods = ("GET", "POST", "HEAD", "OPTIONS")
    authentication_classes = (CsrfExemptSessionAuthentication,)
    pagination_class = MessagePagination

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(
            Q(recipient=request.user) | Q(user=request.user)
        )
        target = self.request.query_params.get("target", None)
        if target is not None:
            self.queryset = self.queryset.filter(
                Q(recipient=request.user, user__username=target)
                | Q(recipient__username=target, user=request.user)
            )
        return super(MessageModelViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        msg = get_object_or_404(
            self.queryset.filter(
                Q(recipient=request.user) | Q(user=request.user), Q(pk=kwargs["pk"])
            )
        )
        serializer = self.get_serializer(msg)
        return Response(serializer.data)


class UserModelViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserModelSerializer
    allowed_methods = ("GET", "HEAD", "OPTIONS")
    pagination_class = None  # Get all users

    def list(self, request, *args, **kwargs):
        # Get all users except yourself
        self.queryset = self.queryset.exclude(id=request.user.id)
        return super(UserModelViewSet, self).list(request, *args, **kwargs)


class ActiveUserModelViewSet(ModelViewSet):
    serializer_class = UserModelSerializer
    allowed_methods = ("GET", "HEAD", "OPTIONS")
    pagination_class = None

    def list(self, request, *args, **kwargs):
        sql_query = f"SELECT * FROM auth_user WHERE id IN ((SELECT DISTINCT user_id FROM auth_user AS u INNER JOIN core_messagemodel AS m ON u.id = m.user_id OR u.id = m.recipient_id WHERE u.id = {request.user.id}) UNION (SELECT DISTINCT recipient_id FROM auth_user AS u INNER JOIN core_messagemodel AS m ON u.id = m.user_id OR u.id = m.recipient_id WHERE u.id = {request.user.id})) AND id != {request.user.id};"
        self.queryset = User.objects.raw(sql_query)
        return super(ActiveUserModelViewSet, self).list(request, *args, **kwargs)
