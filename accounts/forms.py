"""
This module contains custom forms used to collect the information needed to create a model.
"""
from django import forms
from .models import UserInformation, SponsorCompany


class UserInformationForm(forms.ModelForm):
    """
    This form creates an instance of a UserInformation model and collects its fields
    """
    # Fields that will need to be completed in this form
    user_email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'readonly': 'readonly'}))  # read only
    first_name = forms.CharField(label='First Name', max_length=25)
    last_name = forms.CharField(label='Last Name', max_length=25)
    phone_number = forms.IntegerField(label='Phone Number', max_value=9999999999, min_value=1000000000)
    sponsor_company = forms.ModelChoiceField(label='Sponsor', queryset=SponsorCompany.objects.all())


    def __init__(self, *args, **kwargs):
        """function __init__ is called to instantiate the user information form

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super(UserInformationForm, self).__init__(*args, **kwargs)

        # Validator that makes sure all the fields have been filled in
        for _field_name, field in self.fields.items():
            field.required = True

    class Meta:
        """
        A class that stores the meta information about this form
        """
        model = UserInformation
        fields = ['user_email', 'first_name', 'last_name', 'phone_number', 'sponsor_company']



