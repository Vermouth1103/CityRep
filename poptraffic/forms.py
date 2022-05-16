from django import forms

# class RoadNetworkUpload(forms.Form):

#     file = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

#     def clean_file_ext(self):
#         file = self.cleaned_data['file']
#         ext = file.name.split('.')[-1]
#         if ext != 'json':
#             raise forms.ValidationError("Only json files are allowed.")
#         return file

# class TrajectoryUpload(forms.Form):

#     file = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

#     def clean_file_ext(self):
#         file = self.cleaned_data['file']
#         ext = file.name.split('.')[-1]
#         if ext != 'txt':
#             raise forms.ValidationError("Only txt files are allowed.")
#         return file

# class POIUpload(forms.Form):

#     file = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

#     def clean_file_ext(self):
#         file = self.cleaned_data['file']
#         ext = file.name.split('.')[-1]
#         if ext != 'csv':
#             raise forms.ValidationError("Only csv files are allowed.")
#         return file

class PopTrafficDataForm(forms.Form):

    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    type = forms.CharField(label="Data Type", max_length=50,
                                        widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean_file_ext(self):
        file = self.cleaned_data['file']
        ext = file.name.split('.')[-1]
        if ext != 'json':
            raise forms.ValidationError("Only json files are allowed.")
        return file