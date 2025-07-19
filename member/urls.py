from django.conf.urls import  include
from django.urls import path
from . import views

urlpatterns = [
  path('all/', views.MemberList.as_view()),
  path('create/', views.MemberCreate.as_view()),
  path('<int:pk>/', views.MemberDetail.as_view()),
  path('auth/', views.MemberDetail.as_view()), 
  
  # Follow des membres entré en input
  path('follow/', views.FollowMultipleMembersView.as_view()),
  # unfollowUser
  path('unfollow/<int:pk>/', views.UnfollowMemberView.as_view()),
  #Get all following
  path('following/all/', views.FollowingListView.as_view()),
  
  # Forcé des membres entré en input à nous suivre
  path('add-followers/', views.AddFollowersAPIView.as_view()),
  
  
  
  path('esp32-data/', views.ESP32DataView.as_view(), name='esp32-data'),
]
