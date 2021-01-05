from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from authentication.models import User
from b2b.models import customer_management
import os

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Username",                
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder" : "Password",                
                "class": "form-control"
            }
        ))

class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Firstname",                
                "class": "form-control"
            }
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Lastname",                
                "class": "form-control"
            }
        )
    )
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Username",                
                "class": "form-control"
            }
        ))
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
                "placeholder" : "Password check",                
                "class": "form-control"
            }
        ))


    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')


class UserProfileForm(forms.ModelForm):
    ALLOWED_TYPES = ['jpg', 'jpeg', 'png']

    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Firstname",
                "class": "form-control"
            }
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Lastname",
                "class": "form-control"
            }
        )
    )
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    profile_image = forms.FileField(
        widget=forms.FileInput(
            attrs={
                "placeholder": "Profile Image",
                "class": "form-control"
            }
        ),
        required=False,
        help_text="File must be smaller than 4MB. Allowed file types are jpg, jpeg, png"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control",
                "read-only":True
            }
        ))
    # password1 = forms.CharField(
    #     widget=forms.PasswordInput(
    #         attrs={
    #             "placeholder": "Password",
    #             "class": "form-control"
    #         }
    #     ))
    # password2 = forms.CharField(
    #     widget=forms.PasswordInput(
    #         attrs={
    #             "placeholder": "Password check",
    #             "class": "form-control"
    #         }
    #     ))

    class Meta:
        model = User
        fields = ('first_name', 'last_name','profile_image', 'username', 'email') #, 'password1', 'password2')
     
    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image', None)
        if not image:
            raise forms.ValidationError('Missing image file')
        try:
            extension = os.path.splitext(image.name)[1][1:].lower()
            if extension in self.ALLOWED_TYPES:
                if image.size > 4*1024*1024:
                    raise forms.ValidationError("Image file too large ( > 4mb )")
                else:
                    return image
            else:
                raise forms.ValidationError('File types is not allowed')
        except Exception as e:
            print(e)
            raise forms.ValidationError(e)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['email'].widget.attrs['readonly'] = True


class CustomerForm(forms.ModelForm):
    ALLOWED_TYPES = ['jpg', 'jpeg', 'png']
    company_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Business Name",
                "class": "form-control"
            }
        )
    )

    company_logo = forms.FileField(
        widget=forms.FileInput(
            attrs={
                "placeholder": "Business Logo",
                "class": "form-control"
            }
        ),
        required=False,
        help_text="File must be smaller than 4MB. Allowed file types are jpg, jpeg, png"
    )

    business_info = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 2,
                "placeholder": "Business Information",
                "class": "form-control"
            }
        )
    )

    class Meta:
        model = customer_management
        fields = ('company_name', 'company_logo','business_info')


    def clean_company_logo(self):
        image = self.cleaned_data.get('company_logo', None)
        if not image:
            raise forms.ValidationError('Missing image file')
        try:
            extension = os.path.splitext(image.name)[1][1:].lower()
            if extension in self.ALLOWED_TYPES:
                if image.size > 4*1024*1024:
                    raise forms.ValidationError("Image file too large ( > 4mb )")
                return image
            else:
                raise forms.ValidationError('File types is not allowed')
        except Exception as e:
            print(e)
            raise forms.ValidationError(e)


class createChipForm(forms.Form):
    chip_title = forms.CharField(max_length=200,required=True, label="Title", widget=forms.TextInput(attrs={'placeholder': 'Enter chip title', 'class': 'form-control'}))

    start_date = forms.DateTimeField(input_formats=['%d/%m/%Y'],
                                     widget=forms.DateTimeInput(attrs={
                                    'class': 'form-control datetimepicker-input',
                                    'data-target': '#start_date',
                                    'id':'start_date'
                                    }),
                                     label="Start Date",
                                     )
    end_date = forms.DateTimeField(input_formats=['%d/%m/%Y'],
                                     widget=forms.DateTimeInput(attrs={
                                         'class': 'form-control datetimepicker-input',
                                         'data-target': '#end_date',
                                         'id': 'end_date'
                                     }),
                                   label="End Date",
                                   )