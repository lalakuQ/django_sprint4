from django import forms
from .models import Post


class CreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }

