from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    EmployerViewSet, PositionViewSet, UserViewSet, employer_login, employer_signup, get_leave_management, unverified_users,
      update_user_verification, user_detail, user_list, user_login,user_signup, 
    verified_users,apply_leave,approve_leave,reject_leave,get_approved_leaves,get_pending_leaves,get_rejected_leaves,loss_pay,update_user_salary,calculate_payroll,get_user_payroll
)
from payroll_app import views

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'Employers', EmployerViewSet)
router.register(r'Position', PositionViewSet)

urlpatterns = [

    path('signup-apis/user-signup/', user_signup, name='user_signup'),
    path('signup-apis/employer-signup/', employer_signup, name='employer_signup'),

    path('login-apis/users-login/', views.user_login, name='user_login'),
    path('login-apis/employers-login/', employer_login, name='employer_login'),

    path('verfication-apis/unverified/', unverified_users, name='unverified-users'),
    path('verfication-apis/verified/', verified_users, name='unverified-users'),
    path('verfication-apis/update-verification/<int:user_id>/', views.update_user_verification, name='update_user_verification'),

    path('leave-apis/apply-leave/', views.apply_leave, name='apply_leave'),
    path('leave-apis/loss_pay/', views.loss_pay, name='loss_pay'),

    path('approval-apis/approve-leave/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('approval-apis/reject-leave/<int:leave_id>/', views.reject_leave, name='reject_leave'),

    path('api/leave-management/', get_leave_management, name='get_leave_management'),
    path('api/get-pending-leaves/', views.get_pending_leaves, name='get_pending_leaves'),
    path('api/get-approved-leaves/', views.get_approved_leaves, name='get_approved_leaves'),
    path('api/get-rejected-leaves/',get_rejected_leaves, name='get_rejected_leaves'),

    path('salary-apis/update-salary/<int:user_id>/',views.update_user_salary, name='update_user_salary'),
    path('salary-apis/calculate-payroll/',views.calculate_payroll, name='calculate_payroll'),
    path('salary-apis/<int:user_id>/payroll/', get_user_payroll, name='get_user_payroll'),
    
]

# Add the URLs generated by the router
urlpatterns += router.urls
