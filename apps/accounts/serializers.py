# file: apps/accounts/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    company_name    = serializers.CharField(source='company.name',    read_only=True, default=None)
    department_name = serializers.CharField(source='department.name', read_only=True, default=None)

    class Meta:
        model  = Employee
        fields = [
            'id', 'email', 'name', 'role',
            'company', 'company_name',
            'department', 'department_name',
            'is_active', 'date_joined',
        ]
        read_only_fields = ['id', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model  = Employee
        fields = ['email', 'name', 'password', 'role', 'department']

    def create(self, validated_data):
        request  = self.context.get('request')
        password = validated_data.pop('password')
        emp = Employee(**validated_data)
        if request and not request.user.is_superadmin:
            emp.company = request.user.company
        emp.set_password(password)
        emp.save()
        return emp


class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid email or password.')
        if not user.is_active:
            raise serializers.ValidationError('Account is disabled.')
        refresh = RefreshToken.for_user(user)
        return {
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'user':    EmployeeSerializer(user).data,
        }


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_old_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value