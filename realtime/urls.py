from django.urls import path
from . import views

urlpatterns = [
    path('message/', views.ESP32MessageReceiver.as_view()),
    
    # path('add-followers/', views.AddFollowersAPIView.as_view()),
]
