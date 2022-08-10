from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from core.models import ChatUser
from django.contrib.auth.models import User
from django import forms


class RegisterForm(UserCreationForm):
    # def __init__(self, *args, **kwargs):
    #     super(RegisterForm, self).__init__(*args, **kwargs)
    #     self.fields["username"].widget.attrs.pop("autofocus", None)

    avatar = forms.ImageField(label="Avatar", required=False)

    username = forms.CharField(
        label="Username",
        required=True,
        help_text="100 characters max.",
        widget=forms.TextInput(
            attrs={
                "class": "input is-medium",
                "type": "text",
                "placeholder": "Username",
            }
        ),
    )
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.TextInput(
            attrs={"class": "input is-medium", "type": "text", "placeholder": "Email"}
        ),
    )
    password1 = forms.CharField(
        label="Password",
        required=True,
        help_text="100 characters max.",
        widget=forms.PasswordInput(
            attrs={
                "class": "input is-medium",
                "type": "password",
                "placeholder": "Password",
            }
        ),
    )
    password2 = forms.CharField(
        label="Confirm password",
        required=True,
        help_text="100 characters max.",
        widget=forms.PasswordInput(
            attrs={
                "class": "input is-medium",
                "type": "password",
                "placeholder": "Confirm password",
            }
        ),
    )

    class Meta:
        model = ChatUser
        fields = ("username", "email", "avatar")


class LoginForm(AuthenticationForm):

    username = forms.CharField(
        label="Username",
        required=True,
        help_text="100 characters max.",
        widget=forms.TextInput(
            attrs={
                "class": "input is-medium",
                "type": "text",
                "placeholder": "Username",
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        required=True,
        help_text="100 characters max.",
        widget=forms.PasswordInput(
            attrs={
                "class": "input is-medium",
                "type": "password",
                "placeholder": "Password",
            }
        ),
    )

    class Meta:
        model = ChatUser
