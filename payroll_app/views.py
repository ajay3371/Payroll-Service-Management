from datetime import date
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, generics, status
from payroll_app.models import LeaveManagement, PayrollManagement, Position, User, Employer
from payroll_app.seralizers import AnnualSalarySerializer, EmployerLoginSerializer, LeaveManagementSerializer, Payroll_ManagementSerializer, PayrollManagementSerializer_userid, PositionSerializer,UserLoginSerializer, UserSerializer, EmployerSerializer, UserSignupSerializer, EmployerSignupSerializer,LeaveApplicationSerializer
from django.contrib.auth.hashers import make_password,check_password
from drf_yasg.utils import swagger_auto_schema
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import calendar


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class EmployerViewSet(viewsets.ModelViewSet):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer

class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer

@swagger_auto_schema(methods=['post'],request_body=UserSignupSerializer)
@api_view(['POST'])
def user_signup(request):
    if request.method == 'POST':
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            # Hash the password before saving
            validated_data['password'] = make_password(validated_data.get('password'))
            user = User.objects.create(**validated_data)
            # Return serialized user data
            response_serializer = UserSignupSerializer(user)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({'payload': 'Only POST requests are allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@swagger_auto_schema(methods=['post'],request_body=EmployerSignupSerializer)
@api_view(['POST'])
def employer_signup(request):
    if request.method == 'POST':
        serializer = EmployerSignupSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            # Hash the password before saving
            validated_data['password'] = make_password(validated_data.get('password'))
            employer = Employer.objects.create(**validated_data)
            # Return serialized employer data
            response_serializer = EmployerSignupSerializer(employer)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
def user_list(request):
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

@api_view(['DELETE'])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@swagger_auto_schema(methods=['post'],request_body=UserLoginSerializer)
@api_view(['POST'])
def user_login(request):
    email=request.data.get('email')
    password=request.data.get('password')
    try:
        user=User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'payload': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
    if check_password(password,user.password):
        if not user.verified:
            return Response({'payload': 'User is not verified'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'payload': 'login successfull'}, status=status.HTTP_200_OK)
    return Response({'payload': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
@swagger_auto_schema(methods=['post'],request_body=EmployerLoginSerializer)
@api_view(['POST'])
def employer_login(request):
    email=request.data.get('email')
    password=request.data.get('password')
    try:
        employer=Employer.objects.get(email=email)
    except Employer.DoesNotExist:
        return Response({'payload': 'Employer does not exist'}, status=status.HTTP_404_NOT_FOUND)
    if check_password(password,employer.password):
        if not employer.verified:
            return Response({'payload': 'Employer is not verified'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'payload': 'login successfull'}, status=status.HTTP_200_OK)
    return Response({'payload': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        

@swagger_auto_schema(methods=['get'])
@api_view(['GET'])
def unverified_users(request):
    if request.method == 'GET':
        unverified_users = User.objects.filter(verified=False)
        serializer = UserSerializer(unverified_users, many=True)
        return Response(serializer.data)
    
@swagger_auto_schema(methods=['get'])
@api_view(['GET'])
def verified_users(request):
    if request.method == 'GET':
        verified_users = User.objects.filter(verified=True)
        serializer = UserSerializer(verified_users, many=True)
        return Response(serializer.data)




@swagger_auto_schema(methods=['put'],request_body=AnnualSalarySerializer)
@api_view(['PUT'])
def update_user_verification(request, user_id):
    if request.method == 'PUT':
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({'payload': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        salary = request.data.get('annual_salary')
        if salary is not None: 
            user.annual_salary = salary
            user.save()
        user.save()

        if user.verified:
            return Response({'payload': 'User is already verified'}, status=status.HTTP_200_OK)

        position_id = user.position
        position = Position.objects.filter(id=position_id).first()

        if position:
            user.verified = True
            user.save()
            updated_user = UserSerializer(user)
            return Response(updated_user.data, status=status.HTTP_200_OK)
        else:
            return Response({'payload': 'Position not found in Position model'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'payload': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        
        

@swagger_auto_schema(methods=['post'], request_body=LeaveApplicationSerializer)
@api_view(['POST'])
def apply_leave(request):
    if request.method == 'POST':
        serializer = LeaveApplicationSerializer(data=request.data)
        if serializer.is_valid():
            user_id = request.data.get('user')  # Extract user ID from request data
            date_applied = serializer.validated_data.get('date_applied', timezone.now().date())
            user_verified = User.objects.filter(id=user_id, verified=True).first()
            user_leaves = User.objects.filter(id=user_id).first()

            if not user_verified:
                return Response({'payload': 'User not verified'}, status=status.HTTP_400_BAD_REQUEST)

            if date_applied < timezone.now().date():
                return Response({'payload': 'Date applied cannot be in the past'}, status=status.HTTP_400_BAD_REQUEST)

            existing_leave = LeaveManagement.objects.filter(user=user_verified, date_applied=date_applied).first()
            if existing_leave:
                return Response({'payload': 'Leave already applied for the same date'}, status=status.HTTP_400_BAD_REQUEST)

            if user_leaves.leaves > 0:
                leave_obj = LeaveManagement.objects.create(user=user_verified, date_applied=date_applied)
                leave_serializer = LeaveApplicationSerializer(leave_obj)
                return Response(leave_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'payload': 'Not enough leaves available'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['PUT'])
def approve_leave(request, leave_id):
    if request.method == 'PUT':
        try:
            leave_obj = LeaveManagement.objects.get(id=leave_id)
        except LeaveManagement.DoesNotExist:
            return Response({'payload': 'Leave ID does not exist'}, status=status.HTTP_404_NOT_FOUND)
        if leave_obj.leave_status == 'approved':
            return Response({'payload': 'Leave has already been approved'}, status=status.HTTP_400_BAD_REQUEST)
        leave_obj.leave_status = 'approved'
        leave_obj.save()
        user = leave_obj.user
        user.leaves -= 1
        user.save()

        subject = 'Leave Approval'
        html_message = f'''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Leave Approval</title>
            </head>
            <body>
                <p>Hello {user.first_name+' '+user.last_name},</p>
                <p>Your leave application has been approved.</p>
                <p>Thank you.</p>
            </body>
            </html>
        '''
        
        from_email = settings.EMAIL_HOST_USER
        to_email = user.email
        send_mail(subject, '', from_email, [to_email], html_message=html_message)
        return Response({'payload': 'Leave approved successfully'}, status=status.HTTP_200_OK)
  
@api_view(['PUT'])
def reject_leave(request, leave_id):
    if request.method == 'PUT':
        try:
            leave_obj = LeaveManagement.objects.get(id=leave_id)
        except LeaveManagement.DoesNotExist:
            return Response({'payload': 'Leave ID does not exist'}, status=status.HTTP_404_NOT_FOUND)
        if leave_obj.leave_status == 'rejected':
            return Response({'payload': 'Leave has already been rejectd'}, status=status.HTTP_400_BAD_REQUEST)

        leave_obj.leave_status = 'rejected'
        leave_obj.save()
        if leave_obj.leave_status == 'rejected':
            subject = ' Status of Your Leave Approval'
            message = f'Your leave application has been rejected.'
            from_email = settings.EMAIL_HOST_USER
            to_email = leave_obj.user.email
            send_mail(subject, message, from_email, [to_email])
        return Response({'payload': 'Leave rejected'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_leave_management(request):
    if request.method == 'GET':
        leave_management = LeaveManagement.objects.all()
        serializer = LeaveManagementSerializer(leave_management, many=True)
        return Response(serializer.data)
    

@api_view(['GET'])
def get_pending_leaves(request):
    if request.method == 'GET':
        pending_leaves = LeaveManagement.objects.filter(leave_status='pending')
        serializer = LeaveManagementSerializer(pending_leaves, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

@api_view(['GET'])
def get_approved_leaves(request):
    if request.method == 'GET':
        approved_leaves = LeaveManagement.objects.filter(leave_status='approved')
        serializer = LeaveManagementSerializer(approved_leaves, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_rejected_leaves(request):
    if request.method == 'GET':
        rejected_leaves = LeaveManagement.objects.filter(leave_status='rejected')
        serializer = LeaveManagementSerializer(rejected_leaves, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(methods=['post'], request_body=LeaveApplicationSerializer)
@api_view(['POST'])
def loss_pay(request):
    if request.method == 'POST':
        serializer = LeaveApplicationSerializer(data=request.data)
        if serializer.is_valid():
            user_id = request.data.get('user')
            date_applied = serializer.validated_data.get('date_applied', timezone.now().date())
            user_verified = User.objects.filter(id=user_id, verified=True).first()
            user = User.objects.filter(id=user_id).first()

            if not user:
                return Response({'payload': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if not user_verified:
                return Response({'payload': 'User not verified'}, status=status.HTTP_400_BAD_REQUEST)

            if user.leaves > 0:
                return Response({'payload': 'regular leaves are available for this user'}, status=status.HTTP_400_BAD_REQUEST)

            if date_applied < timezone.now().date():
                return Response({'payload': 'Cannot apply leave for past day'}, status=status.HTTP_400_BAD_REQUEST)

            existing_leave = LeaveManagement.objects.filter(user=user, date_applied=date_applied).first()
            if existing_leave:
                return Response({'payload': 'Leave already applied for the same date'}, status=status.HTTP_400_BAD_REQUEST)

            # Update LeaveManagement table
            leave_obj = LeaveManagement.objects.create(user=user_verified, date_applied=date_applied)
            leave_obj.date_applied = date_applied
            leave_obj.save()

            return Response({'payload': 'Leave applied successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
@swagger_auto_schema(methods=['put'],request_body=AnnualSalarySerializer)
@api_view(['PUT'])
def update_user_salary(request, user_id):
    if request.method == 'PUT':
        user = User.objects.filter(id=user_id).first()
        if user.verified:
            salary = request.data.get('annual_salary')
            if salary is not None: 
                user.annual_salary = salary
                user.save()
                return Response({'payload': 'User Salary is Updated'}, status=status.HTTP_200_OK)
        else:
           return Response({'payload': 'User not verified'}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(methods=['post'],request_body=Payroll_ManagementSerializer)
@api_view(['POST'])
def calculate_payroll(request):
    if request.method == 'POST':
        serializer = Payroll_ManagementSerializer(data=request.data)
        if serializer.is_valid():
            user_id = request.data.get('user')
            month = request.data.get('month')
            year = request.data.get('year')

            # Check if user is verified
            user = User.objects.filter(id=user_id, verified=True).first()
            if not user:
                return Response({'error': 'User is not verified'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the month and year are valid (not in the future)
            current_date = date.today()
            if year > current_date.year or (year == current_date.year and month > current_date.month):
                return Response({'payload': 'Cannot calculate for future months/years'}, status=status.HTTP_400_BAD_REQUEST)
            
            existing_payroll = PayrollManagement.objects.filter(user=user, month=month, year=year).exists()
            if existing_payroll:
                return JsonResponse({'payload': 'Payroll record already exists for this user, year, and month'},status=status.HTTP_400_BAD_REQUEST)

            # Calculate the values for the payroll
            annual_salary = user.annual_salary  # Assuming user has an 'annual_salary' field
            gross_salary = annual_salary / 12  # Monthly gross salary
            provident_fund = round(gross_salary * 0.04, 2)  # 4% of gross salary rounded to 2 decimal places
            if gross_salary <= 7500:
                professional_tax = 0
            elif 7501 <= gross_salary <= 10000:
                professional_tax = 175
            else:
                professional_tax = 200
            num_days_in_month = calendar.monthrange(year, month)[1]
            loss_of_pay = round(((gross_salary - provident_fund - professional_tax) / num_days_in_month) * user.leaves, 2) 
            net_salary = round(gross_salary - provident_fund - professional_tax - loss_of_pay, 2)  

            # Update the PayrollManagement instance with the calculated values
            payroll_instance = PayrollManagement.objects.create(
                user=user,
                month=month,
                year=year,
                gross_salary=gross_salary,
                provident_fund=provident_fund,
                professional_tax=professional_tax,
                loss_of_pay=loss_of_pay,
                net_salary=net_salary
            )

            # Prepare the response data
            payroll_data = {
                'user': user_id,
                'month': month,
                'year': year,
                'gross_salary': f'{gross_salary:.2f}',  
                'provident_fund': f'{provident_fund:.2f}', 
                'professional_tax': professional_tax,
                'loss_of_pay': f'{loss_of_pay:.2f}',  
                'net_salary': f'{net_salary:.2f}',  
            }

            return Response(payroll_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_user_payroll(request, user_id):
    payrolls = PayrollManagement.objects.filter(user_id=user_id)
    if not payrolls.exists():
        print(f"No payroll records found for user with ID {user_id}.")
        return Response({"detail": "No payroll records found for this user."}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the payroll data
    serializer = PayrollManagementSerializer_userid(payrolls, many=True)
    # Print payroll data for debuggin
    return Response(serializer.data, status=status.HTTP_200_OK)


