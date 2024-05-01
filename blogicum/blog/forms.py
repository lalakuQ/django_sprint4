from django import forms
from .models import Post


class CreateForm(forms.ModelForm):
    class Meta:
        model = Post
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }
        exclude = ('author',)
