import sqlite3
import json
from datetime import datetime

class DatabaseManager:
    """Менеджер для работы с базой данных кулинарной книги"""
    
    def __init__(self, db_name='cookbook.db'):
        self.db_name = db_name
        self.conn = None
    
    def connect(self):
        """Подключение к базе данных"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row  # Для доступа к колонкам по имени
            return True
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return False
    
    def close(self):
        """Закрытие соединения с базой данных"""
        if self.conn:
            self.conn.close()
    
    # ===== ПОЛЬЗОВАТЕЛИ =====
    
    def create_user(self, email, password, name, avatar='', role='Кулинарный энтузиаст'):
        """Создание нового пользователя"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO users (email, password, name, avatar, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, password, name, avatar, role))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"Пользователь с email {email} уже существует")
            return None
    
    def get_user(self, email):
        """Получение пользователя по email"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def verify_user(self, email, password):
        """Проверка логина и пароля"""
        user = self.get_user(email)
        if user and user['password'] == password:
            return user
        return None
    
    def get_user_by_id(self, user_id):
        """Получение пользователя по ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    # ===== КАТЕГОРИИ =====
    
    def get_categories(self):
        """Получение всех категорий"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT c.*, COUNT(r.id) as recipe_count 
            FROM categories c 
            LEFT JOIN recipes r ON c.id = r.category_id 
            GROUP BY c.id
        ''')
        return [dict(row) for row in cursor.fetchall()]
    
    def get_category(self, category_id):
        """Получение категории по ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM categories WHERE id = ?', (category_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    # ===== РЕЦЕПТЫ =====
    
    def create_recipe(self, title, description, category_id, author_id, 
                     preparation_time, servings, difficulty, image_url='', 
                     tags=None, ingredients=None, steps=None):
        """Создание нового рецепта"""
        try:
            cursor = self.conn.cursor()
            
            # Преобразуем списки в JSON строки
            tags_json = json.dumps(tags or [])
            ingredients_json = json.dumps(ingredients or [])
            steps_json = json.dumps(steps or [])
            
            cursor.execute('''
                INSERT INTO recipes (
                    title, description, category_id, author_id, 
                    preparation_time, servings, difficulty, image_url,
                    tags, ingredients, steps
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                title, description, category_id, author_id,
                preparation_time, servings, difficulty, image_url,
                tags_json, ingredients_json, steps_json
            ))
            
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Ошибка при создании рецепта: {e}")
            return None
    
    def get_recipes(self, limit=100, offset=0, category_id=None, author_id=None):
        """Получение рецептов с фильтрацией"""
        cursor = self.conn.cursor()
        
        query = '''
            SELECT r.*, 
                   c.name as category_name, c.icon as category_icon,
                   u.name as author_name, u.avatar as author_avatar
            FROM recipes r
            JOIN categories c ON r.category_id = c.id
            JOIN users u ON r.author_id = u.id
            WHERE 1=1
        '''
        params = []
        
        if category_id:
            query += ' AND r.category_id = ?'
            params.append(category_id)
        
        if author_id:
            query += ' AND r.author_id = ?'
            params.append(author_id)
        
        query += ' ORDER BY r.created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        recipes = []
        
        for row in cursor.fetchall():
            recipe = dict(row)
            # Преобразуем JSON строки обратно в списки
            recipe['tags'] = json.loads(recipe['tags'])
            recipe['ingredients'] = json.loads(recipe['ingredients'])
            recipe['steps'] = json.loads(recipe['steps'])
            recipes.append(recipe)
        
        return recipes
    
    def get_recipe(self, recipe_id):
        """Получение рецепта по ID"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT r.*, 
                   c.name as category_name, c.icon as category_icon,
                   u.name as author_name, u.avatar as author_avatar,
                   u.email as author_email
            FROM recipes r
            JOIN categories c ON r.category_id = c.id
            JOIN users u ON r.author_id = u.id
            WHERE r.id = ?
        ''', (recipe_id,))
        
        row = cursor.fetchone()
        if row:
            recipe = dict(row)
            recipe['tags'] = json.loads(recipe['tags'])
            recipe['ingredients'] = json.loads(recipe['ingredients'])
            recipe['steps'] = json.loads(recipe['steps'])
            
            # Увеличиваем счетчик просмотров
            cursor.execute('UPDATE recipes SET views = views + 1 WHERE id = ?', (recipe_id,))
            self.conn.commit()
            
            return recipe
        return None
    
    def search_recipes(self, search_term, limit=50):
        """Поиск рецептов"""
        cursor = self.conn.cursor()
        
        query = '''
            SELECT r.*, 
                   c.name as category_name, c.icon as category_icon,
                   u.name as author_name, u.avatar as author_avatar
            FROM recipes r
            JOIN categories c ON r.category_id = c.id
            JOIN users u ON r.author_id = u.id
            WHERE r.title LIKE ? OR r.description LIKE ?
            ORDER BY r.created_at DESC
            LIMIT ?
        '''
        
        search_pattern = f'%{search_term}%'
        cursor.execute(query, (search_pattern, search_pattern, limit))
        
        recipes = []
        for row in cursor.fetchall():
            recipe = dict(row)
            recipe['tags'] = json.loads(recipe['tags'])
            recipe['ingredients'] = json.loads(recipe['ingredients'])
            recipe['steps'] = json.loads(recipe['steps'])
            recipes.append(recipe)
        
        return recipes
    
    # ===== ИЗБРАННОЕ =====
    
    def add_to_favorites(self, user_id, recipe_id):
        """Добавление рецепта в избранное"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO favorites (user_id, recipe_id)
                VALUES (?, ?)
            ''', (user_id, recipe_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении в избранное: {e}")
            return False
    
    def remove_from_favorites(self, user_id, recipe_id):
        """Удаление рецепта из избранного"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM favorites WHERE user_id = ? AND recipe_id = ?', 
                      (user_id, recipe_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_favorites(self, user_id):
        """Получение избранных рецептов пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT r.*, 
                   c.name as category_name, c.icon as category_icon,
                   u.name as author_name
            FROM recipes r
            JOIN favorites f ON r.id = f.recipe_id
            JOIN categories c ON r.category_id = c.id
            JOIN users u ON r.author_id = u.id
            WHERE f.user_id = ?
            ORDER BY f.created_at DESC
        ''', (user_id,))
        
        recipes = []
        for row in cursor.fetchall():
            recipe = dict(row)
            recipe['tags'] = json.loads(recipe['tags'])
            recipe['ingredients'] = json.loads(recipe['ingredients'])
            recipe['steps'] = json.loads(recipe['steps'])
            recipes.append(recipe)
        
        return recipes
    
    def is_favorite(self, user_id, recipe_id):
        """Проверка, находится ли рецепт в избранном"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT 1 FROM favorites WHERE user_id = ? AND recipe_id = ?', 
                      (user_id, recipe_id))
        return cursor.fetchone() is not None
    
    # ===== ОЦЕНКИ =====
    
    def add_rating(self, user_id, recipe_id, value, comment=''):
        """Добавление оценки рецепту"""
        try:
            cursor = self.conn.cursor()
            
            # Обновляем или добавляем оценку
            cursor.execute('''
                INSERT OR REPLACE INTO ratings (user_id, recipe_id, value, comment)
                VALUES (?, ?, ?, ?)
            ''', (user_id, recipe_id, value, comment))
            
            # Обновляем средний рейтинг рецепта
            cursor.execute('''
                UPDATE recipes 
                SET average_rating = (
                    SELECT AVG(value) FROM ratings WHERE recipe_id = ?
                ),
                rating_count = (
                    SELECT COUNT(*) FROM ratings WHERE recipe_id = ?
                )
                WHERE id = ?
            ''', (recipe_id, recipe_id, recipe_id))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении оценки: {e}")
            return False
    
    def get_recipe_ratings(self, recipe_id):
        """Получение всех оценок рецепта"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT r.*, u.name as user_name, u.avatar as user_avatar
            FROM ratings r
            JOIN users u ON r.user_id = u.id
            WHERE r.recipe_id = ?
            ORDER BY r.created_at DESC
        ''', (recipe_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # ===== СТАТИСТИКА =====
    
    def get_statistics(self):
        """Получение статистики по базе данных"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Количество пользователей
        cursor.execute('SELECT COUNT(*) FROM users')
        stats['users_count'] = cursor.fetchone()[0]
        
        # Количество рецептов
        cursor.execute('SELECT COUNT(*) FROM recipes')
        stats['recipes_count'] = cursor.fetchone()[0]
        
        # Количество категорий
        cursor.execute('SELECT COUNT(*) FROM categories')
        stats['categories_count'] = cursor.fetchone()[0]
        
        # Самый популярный рецепт
        cursor.execute('SELECT title, views FROM recipes ORDER BY views DESC LIMIT 1')
        row = cursor.fetchone()
        if row:
            stats['most_viewed_recipe'] = {'title': row[0], 'views': row[1]}
        
        # Самый активный автор
        cursor.execute('''
            SELECT u.name, COUNT(r.id) as recipe_count
            FROM users u
            LEFT JOIN recipes r ON u.id = r.author_id
            GROUP BY u.id
            ORDER BY recipe_count DESC
            LIMIT 1
        ''')
        row = cursor.fetchone()
        if row:
            stats['top_author'] = {'name': row[0], 'recipe_count': row[1]}
        
        return stats

# Пример использования
if __name__ == '__main__':
    # Создаем менеджер базы данных
    db = DatabaseManager()
    
    if db.connect():
        print("✅ Подключение к базе данных успешно")
        
        # Пример: получение статистики
        stats = db.get_statistics()
        print(f"\n📊 Статистика:")
        print(f"  Пользователей: {stats.get('users_count', 0)}")
        print(f"  Рецептов: {stats.get('recipes_count', 0)}")
        print(f"  Категорий: {stats.get('categories_count', 0)}")
        
        # Пример: получение категорий
        categories = db.get_categories()
        print(f"\n📚 Категории ({len(categories)}):")
        for cat in categories[:5]:
            print(f"  {cat['icon']} {cat['name']} - {cat['recipe_count']} рецептов")
        
        # Пример: получение рецептов
        recipes = db.get_recipes(limit=3)
        print(f"\n🍳 Последние рецепты ({len(recipes)}):")
        for recipe in recipes:
            print(f"  {recipe['title']} - {recipe['author_name']}")
        
        db.close()
        print("\n🔌 Соединение с базой данных закрыто")
    else:
        print("❌ Не удалось подключиться к базе данных")
