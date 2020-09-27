from .models import patient
from django import forms
class forgotForm(forms.Form):
    Email = forms.EmailField()

    Email.widget.attrs.update({'class': 'form-control','name' :'search','placeholder':'Email address'})

    def __str__(self):
        return self.Email

class UpdateForm(forms.ModelForm):
    class Meta:
        model = patient
        fields = ('first_name','username','gender','age','email','selfie','last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['selfie'].widget.attrs.update({'class' :'text-center center-block file-upload','type':'file'})
        self.fields['first_name'].widget.attrs.update({'class' :'form-control','type':'text'})
        self.fields['last_name'].widget.attrs.update({'class' :'form-control','type':'text'})
        self.fields['username'].widget.attrs.update({'class' :'form-control','type':'text'})
        self.fields['gender'].widget.attrs.update({'class' :'form-control','type':'text'})
        self.fields['age'].widget.attrs.update({'class' :'form-control','type':'text'})
        #self.fields['mobile'].widget.attrs.update({'class' :'form-control','type':'tel'})
        self.fields['email'].widget.attrs.update({'class' :'form-control','type':'email'})