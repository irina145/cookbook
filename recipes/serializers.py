from rest_framework import serializers
from .models import Recipe, Ingredient, RecipeIngredient

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'unit', 'category']

class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()
    
    class Meta:
        model = RecipeIngredient
        fields = ['id', 'ingredient', 'quantity', 'note']

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'category', 'category_display',
            'cooking_time', 'difficulty', 'difficulty_display', 'servings',
            'image', 'instructions', 'ingredients',
            'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        ingredients_data = self.context['request'].data.get('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('ingredient_id')
            quantity = ingredient_data.get('quantity')
            note = ingredient_data.get('note', '')
            
            if ingredient_id and quantity:
                ingredient = Ingredient.objects.get(id=ingredient_id)
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    quantity=quantity,
                    note=note
                )
        
        return recipe

class RecipeListSerializer(serializers.ModelSerializer):
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'category', 'category_display',
            'cooking_time', 'difficulty', 'difficulty_display', 'servings',
            'image', 'created_at'
        ]