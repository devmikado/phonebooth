# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import forms as django_forms
from django.contrib.auth.password_validation import validate_password
import re


from .models import User




class LoginForm(forms.Form):
    email = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Email",
                "class": "form-control",
                "tabindex":1,
                "autofocus":"autofocus"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder" : "Password",                
                "class": "form-control",
                "tabindex":2
            }
        ))

class SignUpForm(forms.ModelForm):
    
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder" : "Email",                
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder" : "Password",                
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder" : "Confirm Password",                
                "class": "form-control"
            }
        ))


    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs.update(
                {'autofocus': ''})


    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()
        password = cleaned_data.get("password1")
        confirm_password = cleaned_data.get("password2")


        if password != confirm_password:
            self.add_error('password1', "password and confirm_password does not match")
            # raise forms.ValidationError({"password1": "password and confirm_password does not match"})
        else:
            # if re.search('[A-Z]', password)==None and re.search('[0-9]', password)==None and re.search('[^A-Za-z0-9]', password)==None and re.search('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', password)==None:
            
            # # if re.search('[A-Z]', password)==None:
            #     print("---------------ii2------------------?")
            #     self.add_error('password1', "Your password must contain at least 1 uppercase character.")


            try:
                validate_password(password)
            except forms.ValidationError as error:
                print(list(error))
                self.add_error('password1', (list(error))[0])



        


    def save(self, request=None, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data['password2']
        user.set_password(password)
        if commit:
            user.save()
        return user