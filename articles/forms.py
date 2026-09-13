from django import forms

from .models import NewsArticle


class NewsArticleForm(forms.ModelForm):
    class Meta:
        model = NewsArticle
        fields = ['title', 'slug', 'content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }
