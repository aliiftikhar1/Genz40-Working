from django import forms
from django.contrib.auth.forms import UserCreationForm
from backend.models import CustomUser, PostContactUs, PostSubscribers


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    role = forms.CharField(required=True)
    

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'role']


class LoginForm(forms.ModelForm):
    
    email = forms.EmailField(required=True)
    password = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password']


class PostSubscribeForm(forms.ModelForm):
    class Meta:
        model = PostSubscribers
        fields = ['email']


class PostContactForm(forms.ModelForm):
    class Meta:
        model = PostContactUs
        fields = ['name', 'email', 'phone_number', 'car', 'comments']