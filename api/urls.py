from django.urls import path
from api.views import SignUpAPIView, VerifyUserAPIView, GetNewVerification

urlpatterns = [
    path('register/', SignUpAPIView.as_view()),
    path('verify-user/', VerifyUserAPIView.as_view()),
    path('new-verify/', GetNewVerification.as_view()),
]
