# recipes/management/commands/seed_data.py
from django.core.management.base import BaseCommand
from recipes.models import Recipe, Ingredient, RecipeIngredient
import random

class Command(BaseCommand):
    help = 'Заполняет базу тестовыми данными'
    
    def handle(self, *args, **kwargs):
        # Очищаем существующие данные
        RecipeIngredient.objects.all().delete()
        Recipe.objects.all().delete()
        Ingredient.objects.all().delete()
        
        # Создаем ингредиенты
        ingredients_data = [
            {'name': 'Картофель', 'unit': 'г', 'category': 'vegetables'},
            {'name': 'Лук', 'unit': 'г', 'category': 'vegetables'},
            {'name': 'Морковь', 'unit': 'г', 'category': 'vegetables'},
            {'name': 'Курица', 'unit': 'г', 'category': 'meat'},
            {'name': 'Свинина', 'unit': 'г', 'category': 'meat'},
            {'name': 'Говядина', 'unit': 'г', 'category': 'meat'},
            {'name': 'Помидор', 'unit': 'г', 'category': 'vegetables'},
            {'name': 'Огурец', 'unit': 'г', 'category': 'vegetables'},
            {'name': 'Мука', 'unit': 'г', 'category': 'groceries'},
            {'name': 'Сахар', 'unit': 'г', 'category': 'groceries'},
            {'name': 'Соль', 'unit': 'ч.л.', 'category': 'spices'},
            {'name': 'Перец', 'unit': 'ч.л.', 'category': 'spices'},
            {'name': 'Молоко', 'unit': 'мл', 'category': 'dairy'},
            {'name': 'Яйца', 'unit': 'шт', 'category': 'dairy'},
            {'name': 'Сметана', 'unit': 'г', 'category': 'dairy'},
            {'name': 'Масло растительное', 'unit': 'ст.л.', 'category': 'groceries'},
            {'name': 'Лимон', 'unit': 'шт', 'category': 'fruits'},
            {'name': 'Яблоко', 'unit': 'шт', 'category': 'fruits'},
            {'name': 'Мед', 'unit': 'ст.л.', 'category': 'groceries'},
            {'name': 'Кофе', 'unit': 'ч.л.', 'category': 'groceries'},
        ]
        
        ingredients = {}
        for data in ingredients_data:
            ingredient = Ingredient.objects.create(**data)
            ingredients[data['name']] = ingredient
        
        # Создаем рецепты
        recipes_data = [
            {
                'title': 'Куриный суп',
                'description': 'Наваристый куриный суп с овощами',
                'category': 'soups',
                'cooking_time': 60,
                'difficulty': 2,
                'servings': 4,
                'instructions': '1. Отварить курицу\n2. Добавить овощи\n3. Варить до готовности\n4. Посолить и поперчить',
                'ingredients': [
                    ('Курица', 500),
                    ('Картофель', 300),
                    ('Морковь', 100),
                    ('Лук', 100),
                    ('Соль', 1),
                    ('Перец', 0.5),
                ]
            },
            {
                'title': 'Омлет',
                'description': 'Простой и вкусный завтрак',
                'category': 'breakfast',
                'cooking_time': 15,
                'difficulty': 1,
                'servings': 2,
                'instructions': '1. Взбить яйца с молоком\n2. Посолить\n3. Жарить на сковороде до готовности',
                'ingredients': [
                    ('Яйца', 4),
                    ('Молоко', 100),
                    ('Соль', 0.5),
                    ('Масло растительное', 1),
                ]
            },
            {
                'title': 'Салат из помидоров и огурцов',
                'description': 'Свежий летний салат',
                'category': 'salads',
                'cooking_time': 10,
                'difficulty': 1,
                'servings': 2,
                'instructions': '1. Нарезать овощи\n2. Заправить сметаной\n3. Посолить по вкусу',
                'ingredients': [
                    ('Помидор', 300),
                    ('Огурец', 200),
                    ('Сметана', 50),
                    ('Соль', 0.5),
                ]
            },
            {
                'title': 'Кофе',
                'description': 'Ароматный кофе',
                'category': 'drinks',
                'cooking_time': 5,
                'difficulty': 1,
                'servings': 1,
                'instructions': '1. Сварить кофе\n2. Добавить сахар по вкусу',
                'ingredients': [
                    ('Кофе', 2),
                    ('Сахар', 10),
                ]
            },
            {
                'title': 'Яблочный пирог',
                'description': 'Домашний яблочный пирог',
                'category': 'desserts',
                'cooking_time': 90,
                'difficulty': 4,
                'servings': 8,
                'instructions': '1. Приготовить тесто\n2. Добавить яблоки\n3. Выпекать в духовке 40 минут',
                'ingredients': [
                    ('Яблоко', 500),
                    ('Мука', 300),
                    ('Сахар', 200),
                    ('Яйца', 2),
                    ('Масло растительное', 50),
                ]
            },
        ]
        
        for recipe_data in recipes_data:
            recipe = Recipe.objects.create(
                title=recipe_data['title'],
                description=recipe_data['description'],
                category=recipe_data['category'],
                cooking_time=recipe_data['cooking_time'],
                difficulty=recipe_data['difficulty'],
                servings=recipe_data['servings'],
                instructions=recipe_data['instructions'],
            )
            
            for ingredient_name, quantity in recipe_data['ingredients']:
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ingredients[ingredient_name],
                    quantity=quantity,
                    note=''
                )
        
        self.stdout.write(self.style.SUCCESS(
            f'Создано {Recipe.objects.count()} рецептов и {Ingredient.objects.count()} ингредиентов'
        ))