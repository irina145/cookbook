import os
import sys
import django

# Настраиваем Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    django.setup()
    print("✅ Django настроен")
except Exception as e:
    print(f"❌ Ошибка Django: {e}")
    sys.exit(1)

# Создаем необходимые модели
from django.db import models

# Проверяем и создаем модель Recipe
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipes_recipe (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200),
                description TEXT,
                category VARCHAR(100),
                cooking_time INTEGER
            )
        """)
        print("✅ Таблица рецептов создана")
except Exception as e:
    print(f"⚠️ Ошибка таблицы: {e}")

# Добавляем тестовые данные
try:
    from django.db import connection
    with connection.cursor() as cursor:
        # Проверяем, есть ли уже данные
        cursor.execute("SELECT COUNT(*) FROM recipes_recipe")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Добавляем тестовые рецепты
            test_recipes = [
                ("Крем-суп из тыквы", "Нежный сливочный суп с ароматными специями", "Супы", 45),
                ("Лосось в сливочном соусе", "Нежное филе лосося под сливочно-укропным соусом", "Основные блюда", 30),
                ("Греческий салат", "Классический салат со свежими овощами и сыром фета", "Салаты", 20),
                ("Тирамису", "Итальянский десерт с кофейной пропиткой", "Десерты", 60),
                ("Мохито", "Освежающий коктейль с мятой и лаймом", "Напитки", 10),
                ("Французский тост", "Хрустящий тост с корицей и кленовым сиропом", "Завтраки", 15),
                ("Круассаны", "Слоеная выпечка с шоколадной начинкой", "Выпечка", 90)
            ]
            
            cursor.executemany(
                "INSERT INTO recipes_recipe (title, description, category, cooking_time) VALUES (?, ?, ?, ?)",
                test_recipes
            )
            print(f"✅ Добавлено {len(test_recipes)} тестовых рецептов")
        else:
            print(f"ℹ️ В базе уже есть {count} рецептов")
            
except Exception as e:
    print(f"❌ Ошибка добавления данных: {e}")

print("\n🎉 API готов к работе!")
print("Запустите сервер: python manage.py runserver")