from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.template import loader

from .email import resetting_email
from .models import CustomUser


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(label="",
                               widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 500px; '
                                                                                               'margin-bottom: '
                                                                                               '15px;',
                                                             'placeholder': 'Enter username'}))

    first_name = forms.CharField(label="",
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 500px; '
                                                                                                 'margin-bottom: '
                                                                                                 '15px;',
                                                               'placeholder': 'Enter First Name'}))

    last_name = forms.CharField(label="",
                                widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 500px; '
                                                                                                'margin-bottom: '
                                                                                                '15px;',
                                                              'placeholder': 'Enter Last Name'}))

    phone = forms.CharField(label="", required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 500px; '
                                                                                            'margin-bottom: '
                                                                                            '15px;',
                                                          'placeholder': 'Enter phone'}))

    email = forms.EmailField(label="", widget=forms.EmailInput(attrs={'class': 'form-control', 'style': 'width: 500px; '
                                                                                                        'margin-bottom: 15px;',
                                                                      'placeholder': 'Enter email'}))

    password = forms.CharField(label="",
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'style': 'width: 500px; '
                                                                                                   'margin-bottom: ''15px',
                                                                 'placeholder': 'Enter password'}))

    password2 = forms.CharField(label="",
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'style': 'width: 500px; '
                                                                                                    'margin-bottom: '
                                                                                                    '15px;',
                                                                  'placeholder': 'Confirm the password'}))

    seller_or_customer = forms.ChoiceField(label='',
                                           widget=forms.Select(choices=('customer', 'seller'), attrs={'class': 'form-control', 'style': 'width: 500px; '
                                                                                                        'margin'
                                                                                                        '-bottom: '
                                                                                                        '15px;'}))

    class Meta:
        model = CustomUser
        fields = ["username", "first_name", "last_name", "phone", "email", "seller_or_customer"]

    def clean_password2(self):
        cd = self.cleaned_data
        password1 = cd.get("password")
        password2 = cd.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password mismatch!")
        return password2


class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)
        resetting_email(to_email, context['user'].get_username(), subject, body)
