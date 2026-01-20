from django.db import models

class Recipe(models.Model):
    CATEGORY_CHOICES = [
        ('Супы', 'Супы'),
        ('Основные блюда', 'Основные блюда'),
        ('Салаты', 'Салаты'),
        ('Десерты', 'Десерты'),
        ('Завтраки', 'Завтраки'),
        ('Напитки', 'Напитки'),
        ('Выпечка', 'Выпечка'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    cooking_time = models.IntegerField(verbose_name="Время приготовления (мин)")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Основные блюда', verbose_name="Категория")
    
    def __str__(self):
        return self.title