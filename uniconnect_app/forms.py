from django import forms

from .models import Post
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm,CharField


class TilForm(forms.Form):
    subject = forms.CharField(label='Title', max_length=160)
    content = forms.CharField(label='Content',
                              widget=forms.Textarea, max_length=800)
    # four tags separated by a comma
    tags = forms.CharField(label='Tags (comma separated, maximum: 4)',
                           required=False,
                           max_length=43)
    public = forms.BooleanField(label='Public', required=False)



class RegisterForm(UserCreationForm):
    email = forms.EmailField(max_length=150, help_text='Required',)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        username = self.cleaned_data["username"]
        email = self.cleaned_data['email']
        users = User.objects.filter(email__iexact=email).exclude(username__iexact=username)
        if users:
            raise forms.ValidationError('A user with that email already exists.')
        return email.lower()

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return data



class ResetPasswordForm(forms.Form):
    email = forms.EmailField(max_length=150, help_text='Required')


class SelectForm(forms.Form):
    OPTIONS = (
        ("Oldest", "oldest"),
        ("Newest", "newest"),
        ("Popular", "popular"),
    )
    order = forms.ChoiceField(choices=OPTIONS)
