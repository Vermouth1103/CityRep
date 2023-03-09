from django import forms

class RoutePlanDataForm(forms.Form):

    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    def clean_file_ext(self):
        file = self.cleaned_data['file']
        ext = file.name.split('.')[-1]
        if ext != 'json':
            raise forms.ValidationError("Only json files are allowed.")
        return file
    
class RoutePlanHyperparameterForm(forms.Form):

    # hyperparameter
    epochs = forms.IntegerField(initial=100)
    batch_size = forms.IntegerField(initial=300)
    lr = forms.FloatField(initial=1e-4)
    dropout = forms.FloatField(initial=0.6)

class RoutePlanPredForm(forms.Form):

    start = forms.IntegerField(initial=1)
    end = forms.IntegerField(initial=2)

class NextLocDataForm(forms.Form):

    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    def clean_file_ext(self):
        file = self.cleaned_data['file']
        ext = file.name.split('.')[-1]
        if ext != 'json':
            raise forms.ValidationError("Only json files are allowed.")
        return file
    
class NextLocHyperparameterForm(forms.Form):

    # hyperparameter
    epochs = forms.IntegerField(initial=100)
    batch_size = forms.IntegerField(initial=300)
    lr = forms.FloatField(initial=1e-4)
    dropout = forms.FloatField(initial=0.6)

class NextLocPredForm(forms.Form):

    traj_seq = forms.CharField(label="Traj Seq", max_length=50,
                                        widget=forms.TextInput(attrs={'class': 'form-control'}))
    steps = forms.IntegerField(initial=1)