# file: apps/accounts/views.py
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema

from .models import Employee
from .serializers import (
    LoginSerializer, RegisterSerializer,
    EmployeeSerializer, ChangePasswordSerializer,
)
from .permissions import IsAdminOrAbove
from apps.core.utils import success_response, error_response


@extend_schema(tags=['auth'])
class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="Login — returns JWT access + refresh tokens")
    def post(self, request):
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(success_response(s.validated_data, 'Login successful'))


@extend_schema(tags=['auth'])
class LogoutView(APIView):
    @extend_schema(summary="Logout — blacklists refresh token")
    def post(self, request):
        try:
            RefreshToken(request.data.get('refresh')).blacklist()
            return Response(success_response({}, 'Logged out'), status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(error_response('Invalid token'), status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['auth'])
class MeView(APIView):
    @extend_schema(summary="Get my profile")
    def get(self, request):
        return Response(success_response(EmployeeSerializer(request.user).data))

    @extend_schema(summary="Update my profile")
    def patch(self, request):
        s = EmployeeSerializer(request.user, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(success_response(s.data, 'Profile updated'))


@extend_schema(tags=['auth'])
class ChangePasswordView(APIView):
    @extend_schema(summary="Change password")
    def post(self, request):
        s = ChangePasswordSerializer(data=request.data, context={'request': request})
        s.is_valid(raise_exception=True)
        request.user.set_password(s.validated_data['new_password'])
        request.user.save()
        return Response(success_response({}, 'Password changed'))


@extend_schema(tags=['employees'])
class EmployeeViewSet(ModelViewSet):
    permission_classes = [IsAdminOrAbove]
    search_fields      = ['name', 'email']
    ordering_fields    = ['name', 'date_joined']

    def get_serializer_class(self):
        return RegisterSerializer if self.action == 'create' else EmployeeSerializer

    def get_queryset(self):
        u  = self.request.user
        qs = Employee.objects.select_related('company', 'department')
        return qs.all() if u.is_superadmin else qs.filter(company=u.company)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()