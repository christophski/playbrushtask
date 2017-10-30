from django import forms

class FileUploadForm(forms.Form):
    rawdata = forms.FileField()
    groups = forms.FileField()
