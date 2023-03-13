from django import forms

class AccidentDataForm(forms.Form):

    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    def clean_file_ext(self):
        file = self.cleaned_data['file']
        ext = file.name.split('.')[-1]
        if ext != 'json':
            raise forms.ValidationError("Only json files are allowed.")
        return file

class AccidentPredForm(forms.Form):

    road = forms.IntegerField(initial=100)
    time = forms.IntegerField(initial=10)