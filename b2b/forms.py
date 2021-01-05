from django import forms        
from .models import canned_response_management


class cannedResponseForm(forms.ModelForm):
    positive_response_text = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 2,
                "placeholder": "Write Positive Reponse Here...",
                "class": "form-control"
            }
        )
    )

    negative_response_text = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 2,
                "placeholder": "Write Negative Reponse Here...",
                "class": "form-control"
            }
        )
    )

    neutral_response_text = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 2,
                "placeholder": "Write Neutral Reponse Here...",
                "class": "form-control"
            }
        )
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['positive_response_text'].widget.attrs['placeholder'] = 'Positive Reponse'


    class Meta:
        model = canned_response_management
        fields = ['positive_response_text', 'negative_response_text', 'neutral_response_text']
        
    # positive_response_text = forms.CharField(
    #     widget=forms.TextInput(
    #         attrs={
    #             "placeholder" : "Positive Response",                
    #             "class": "form-control"
    #         }
    #     ))
    
    # negative_response_text = forms.CharField(
    #     widget=forms.TextInput(
    #         attrs={
    #             "placeholder" : "Negative Response",                
    #             "class": "form-control"
    #         }
    #     ))

    # neutral_response_text = forms.CharField(
    #     widget=forms.TextInput(
    #         attrs={
    #             "placeholder" : "Neutral Response",                
    #             "class": "form-control"
    #         }
    #     ))

class createPersonaForm(forms.Form):
        chip_title = forms.CharField(max_length=200, required=True, label="Title", widget=forms.TextInput(
            attrs={'placeholder': 'Enter chip title', 'class': 'form-control'}))

        start_date = forms.DateTimeField(input_formats=['%d/%m/%Y'],
                                         widget=forms.DateTimeInput(attrs={
                                             'class': 'form-control datepicker',
                                             'data-target': '#start_date',
                                             'id': 'start_date'
                                         }),
                                         label="Start Date",
                                         )
        end_date = forms.DateTimeField(input_formats=['%d/%m/%Y'],
                                       widget=forms.DateTimeInput(attrs={
                                           'class': 'form-control datepicker',
                                           'data-target': '#end_date',
                                           'id': 'end_date'
                                       }),
                                       label="End Date",
                                       )
