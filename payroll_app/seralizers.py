from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import LeaveManagement, PayrollManagement, User, Employer,Position
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = '__all__'

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password', 'position']

    def create(self, validated_data):
        password = validated_data.pop('password')
        hashed_password = make_password(password)  # Hash the password
        user = User.objects.create(password=hashed_password, **validated_data)
        return user



class EmployerSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Employer
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        hashed_password=make_password(password)
        employer = Employer.objects.create(password=hashed_password, **validated_data)
        return employer


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()


class EmployerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)

class LeaveApplicationSerializer(serializers.ModelSerializer):
    date_applied = serializers.DateField()

    class Meta:
        model = LeaveManagement
        fields = ['user', 'date_applied']



class LeaveManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveManagement
        fields = ['id', 'user_id','leave_status','date_applied']

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Position
        fields='__all__'

class AnnualSalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['annual_salary']


class Payroll_ManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollManagement
        fields = ['user', 'month', 'year']
    
class PayrollManagementSerializer_userid(serializers.ModelSerializer):
    class Meta:
        model = PayrollManagement
        fields = '__all__'


        
