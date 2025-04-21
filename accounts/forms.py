from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from .models import Profile


class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)
    mobile_phone = forms.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                regex=r"^01[0125][0-9]{8}$",
                message="Enter a valid Egyptian phone number.",
            )
        ],
        required=True,
    )
    profile_picture = forms.ImageField(required=False)

    # Validate that the password and confirm_password match
    def clean_confirm_password(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("confirm_password")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        return password2


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]  


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "mobile_phone",
            "profile_picture",
            "birth_date",
            "facebook",
            "country",
        ]
