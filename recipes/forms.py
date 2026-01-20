from django import forms
from .models import Recipe, Comment

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            'title', 'description', 'category', 'cuisine', 
            'difficulty', 'prep_time', 'cook_time', 'servings',
            'ingredients', 'instructions', 'image'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'ingredients': forms.Textarea(attrs={'rows': 6}),
            'instructions': forms.Textarea(attrs={'rows': 10}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Напишите ваш комментарий...'
            }),
        }