# backend/forms.py
from .models import CustomUser, PostPackage, PostNavItem, PostPaint, PostCharging, PostPart, PostPackageFeature, PostPackageDetail, \
    PostImage, PostSubscribers
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_first_name'}))
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    role = forms.CharField(required=True)
      
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2', 'country', 'role']


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'})
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("There is no user registered with the specified email address.")
        return email
    

class CustomPasswordResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='',
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='',
    )
    

class PostPackageForm(forms.ModelForm):
    class Meta:
        model = PostPackage
        fields = ['name', 'amount', 'description', 'image', 'is_active']

    image = forms.ImageField(required=False)
    # nav_item = forms.CharField(required=False)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     vehicles_parent = PostNavItem.objects.filter(title="Vehicles").first()
    #     if vehicles_parent:
    #         self.fields['nav_item'].queryset = PostNavItem.objects.filter(parent=vehicles_parent)
    #     else:
    #         self.fields['nav_item'].queryset = PostNavItem.objects.none()
    # nav_item = forms.ModelChoiceField(queryset=PostNavItem.objects.filter(related_name='children'), required=True)


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ImageModelForm(forms.ModelForm):
    # image = MultipleFileField(label='Select files', required=False)

    class Meta:
        model = PostImage
        fields = ['image', 'nav_item']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            vehicles_parent = PostNavItem.objects.filter(title="Vehicles").first()
            if vehicles_parent:
                self.fields['nav_item'].queryset = PostNavItem.objects.filter(parent=vehicles_parent)
            else:
                self.fields['nav_item'].queryset = PostNavItem.objects.none()


class PostNavItemForm(forms.ModelForm):
    class Meta:
        model = PostNavItem
        fields = ['title', 'slug', 'content', 'parent', 'is_active']


class PostPackageDetailForm(forms.ModelForm):
    class Meta:
        model = PostPackageDetail
        fields = ['service_type', 'description', 'is_active']


class PostPackageFeatureForm(forms.ModelForm):
    class Meta:
        model = PostPackageFeature
        fields = ['name', 'description', 'amount', 'is_active']


class PostPartForm(forms.ModelForm):
    class Meta:
        model = PostPart
        fields = ['parts_name', 'parts_desc', 'amount', 'file', 'is_active']

    file = forms.ImageField(required=False)


class PostChargingForm(forms.ModelForm):
    class Meta:
        model = PostCharging
        fields = ['charging_name', 'charging_desc', 'amount', 'file', 'is_active']

    file = forms.ImageField(required=False)


class PostPaintForm(forms.ModelForm):
    class Meta:
        model = PostPaint
        fields = ['paint_name', 'paint_desc', 'file', 'amount', 'is_active']

    file = forms.ImageField(required=False)

