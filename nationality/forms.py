
from django import forms


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