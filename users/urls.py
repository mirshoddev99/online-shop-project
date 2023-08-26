from django.urls import path
from .views import RegisterView, CustomLoginView, CustomLogOutView, ContactView, ProfileView, EditProfileView, \
    CustomerAddressView, CustomerAddressEditView, TestRegisterView, CustomPasswordResetView

from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

urlpatterns = [
    path("registration/", RegisterView.as_view(), name="register_page"),
    path("test-registration/", TestRegisterView.as_view(), name="test_register_page"),
    path("login/", CustomLoginView.as_view(), name="login_page"),
    path("logout/", CustomLogOutView.as_view(), name="logout_page"),

    path('password-change/', PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),


    path('contact/', ContactView.as_view(), name='contact_page'),
    path("user-profile/<str:username>", ProfileView.as_view(), name="profile_page"),
    path("edit-profile/", EditProfileView.as_view(), name="edit_profile_page"),
    path("customer-address/", CustomerAddressView.as_view(), name="address_page"),
    path("customer-address-edit/", CustomerAddressEditView.as_view(), name="edit_address_page"),

]
