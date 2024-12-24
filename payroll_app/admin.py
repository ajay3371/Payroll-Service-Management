from django.contrib import admin
from .models import User, Employer, LeaveManagement,Position

admin.site.register(User)
admin.site.register(Employer)
admin.site.register(Position)
admin.site.register(LeaveManagement)

# Register your models here.
