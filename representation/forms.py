from django import forms

class DataForm(forms.Form):

    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    type = forms.CharField(label="Data Type", max_length=50,
                                        widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean_file_ext(self):
        file = self.cleaned_data['file']
        ext = file.name.split('.')[-1]
        if ext != 'json':
            raise forms.ValidationError("Only json files are allowed.")
        return file
    
class HyperparameterForm(forms.Form):

    # hyperparameter
    epochs = forms.IntegerField(initial=100)
    batch_size = forms.IntegerField(initial=300)
    lr = forms.FloatField(initial=1e-4)
    dropout = forms.FloatField(initial=0.6)

    # road_hp
    road_num = forms.IntegerField(initial=1000)
    road_dim = forms.IntegerField(initial=512)

    # region_hp
    region_num = forms.IntegerField(initial=60)
    region_dim = forms.IntegerField(initial=608)

    # zone_hp
    zone_num = forms.IntegerField(initial=20)
    zone_dim = forms.IntegerField(initial=256)