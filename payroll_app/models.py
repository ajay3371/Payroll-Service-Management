import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Position(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'position'

class User(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=12, blank=True, null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    verified = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now)
    position = models.IntegerField(default=0)
    leaves = models.IntegerField(default=10)
    annual_salary = models.IntegerField(default=0)

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'user'

class Employer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=10, default='')
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    verified = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = 'employer'



class LeaveManagement(models.Model):
    user = models.ForeignKey(User, related_name='leave_management', on_delete=models.CASCADE, null=True, blank=True)
    leave_status = models.CharField(max_length=50, default='pending')
    date_applied = models.DateField(default=timezone.now)  # Use DateField instead of DateTimeField

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.date_applied}"

    class Meta:
        db_table = 'leave_management'


def year_choices():
    return [(r,r) for r in range(1984, datetime.date.today().year+1)]

def current_year():
    return datetime.date.today().year


class PayrollManagement(models.Model):
    MONTH_CHOICES = (
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'),
    )
    
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.IntegerField( 
        choices=year_choices(), 
        default=current_year()
    )

    month = models.IntegerField(choices=MONTH_CHOICES)
    gross_salary = models.FloatField(null=True, blank=True)
    provident_fund = models.FloatField(null=True, blank=True)
    professional_tax = models.FloatField(null=True, blank=True)
    loss_of_pay = models.FloatField(default=0.00)
    # income_tax = models.IntegerField()
    net_salary = models.FloatField(null=True, blank=True)
    
    
    def __str__(self):
        return f"{self.user}"
    
    class Meta:
        db_table = 'payroll-management'





