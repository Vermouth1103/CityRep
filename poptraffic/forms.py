from django import forms

class SpeedPredictionDataForm(forms.Form):

    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    def clean_file_ext(self):
        file = self.cleaned_data['file']
        ext = file.name.split('.')[-1]
        if ext != 'json':
            raise forms.ValidationError("Only json files are allowed.")
        return file
    
class SpeedPredictionHyperparameterForm(forms.Form):

    # hyperparameter
    epochs = forms.IntegerField(initial=100)
    batch_size = forms.IntegerField(initial=300)
    lr = forms.FloatField(initial=1e-4)
    dropout = forms.FloatField(initial=0.6)

class FlowPredictionDataForm(forms.Form):

    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    def clean_file_ext(self):
        file = self.cleaned_data['file']
        ext = file.name.split('.')[-1]
        if ext != 'json':
            raise forms.ValidationError("Only json files are allowed.")
        return file
    
class FlowPredictionHyperparameterForm(forms.Form):

    # hyperparameter
    epochs = forms.IntegerField(initial=100)
    batch_size = forms.IntegerField(initial=300)
    lr = forms.FloatField(initial=1e-4)
    dropout = forms.FloatField(initial=0.6)