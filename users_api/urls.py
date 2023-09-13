from django.urls import path
from users_api.views import SignUpAPIView, VerifyUserAPIView, GetNewVerification, UpdateUserInfoAPIView, \
    UserLoginAPIView, \
    UserLoginRefreshAPIView, UserLogoutAPIView, CreateUserAddressAPIView, UserAddressRetrieveDestroyUpdateAPIView, \
    CreatePaymentCardAPIView, CRUDPaymentCardAPIView

urlpatterns = [
    path('register/', SignUpAPIView.as_view()),
    path('verify-user/', VerifyUserAPIView.as_view()),
    path('new-verify/', GetNewVerification.as_view()),
    path('update-user-info/', UpdateUserInfoAPIView.as_view()),
    path('user-login/', UserLoginAPIView.as_view()),
    path('user-login-refresh/', UserLoginRefreshAPIView.as_view()),
    path('user-logout/', UserLogoutAPIView.as_view()),
    path('user-address/', CreateUserAddressAPIView.as_view()),
    path('user-address-crud/<int:id>/', UserAddressRetrieveDestroyUpdateAPIView.as_view()),
    path('user-payment-card/', CreatePaymentCardAPIView.as_view()),
    path('crud-payment-card/<int:id>/', CRUDPaymentCardAPIView.as_view()),

]
