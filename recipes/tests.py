from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Recipe, Ingredient, RecipeIngredient

class RecipeTests(APITestCase):
    def setUp(self):
        # Создаем тестовые ингредиенты
        self.ingredient1 = Ingredient.objects.create(
            name='Картофель',
            unit='г',
            category='vegetables'
        )
        self.ingredient2 = Ingredient.objects.create(
            name='Лук',
            unit='г',
            category='vegetables'
        )
        
        # Создаем тестовый рецепт
        self.recipe = Recipe.objects.create(
            title='Тестовый рецепт',
            description='Описание тестового рецепта',
            category='main',
            cooking_time=30,
            difficulty=2,
            servings=4,
            instructions='Инструкции по приготовлению'
        )
        
        # Добавляем ингредиенты к рецепту
        RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient1,
            quantity=500
        )
        RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient2,
            quantity=100,
            note='мелко нарезанный'
        )
    
    def test_get_recipes(self):
        url = reverse('recipe-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_recipe_detail(self):
        url = reverse('recipe-detail', args=[self.recipe.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Тестовый рецепт')
    
    def test_get_categories(self):
        url = reverse('recipe-categories')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
    
    def test_search_by_ingredients(self):
        url = reverse('recipe-search-by-ingredients') + '?ingredients=картофель'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_quick_recipes(self):
        url = reverse('recipe-quick-recipes')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)