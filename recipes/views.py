from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Recipe

def home(request):
    recipes = list(Recipe.objects.all().values('id', 'title', 'description', 'cooking_time', 'category'))
    return render(request, 'recipes/home.html', {
        'recipes': recipes,
        'recipes_json': recipes  # Для передачи в JavaScript
    })

def recipe_list(request):
    recipes = Recipe.objects.all()
    return render(request, 'recipes/recipe_list.html', {'recipes': recipes})

def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})