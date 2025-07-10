from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
  path('login/', views.CustomLogin.as_view()),
  # path('login_by_email/', views.CustomLoginByEmail.as_view()),
  path('logout/', views.Logout.as_view()),
  path('register/', views.Register.as_view()),
  # path('register_by_email/', views.RegisterByEmail.as_view()),
  path('forget_password/', views.ForgetPassword.as_view()),
  path('change_user_info/changeMail/', views.ChangeUserInfoMail.as_view()),
  path('change_user_info/changePassword/', views.ChangeUserInfoPassword.as_view()),
  path('change_user_info/resetPassword/', views.ChangeUserResetPassword.as_view()),
  path('change_user_info/verifyResetPasswordToken/', views.VerifyResetPasswordToken.as_view()),
]