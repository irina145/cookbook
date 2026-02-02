from flask import Flask, jsonify, request, session
from flask_cors import CORS
import sqlite3
import json

app = Flask(__name__)
app.secret_key = 'super-secret-key'
CORS(app, supports_credentials=True)

def get_db():
    """Подключение к базе данных"""
    conn = sqlite3.connect('recipes.db')
    conn.row_factory = sqlite3.Row
    return conn

# ========== ГЛАВНАЯ СТРАНИЦА ==========
@app.route('/')
def index():
    return "Flask сервер работает! Используйте /api/... для доступа к API"

# ========== АВТОРИЗАЦИЯ ==========
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO users (email, name, password, avatar)
        VALUES (?, ?, ?, ?)
        ''', (data['email'], data['name'], data['password'], data['name'][0]))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        session['user_id'] = user_id
        return jsonify({
            'success': True,
            'user': {
                'id': user_id,
                'email': data['email'],
                'name': data['name'],
                'avatar': data['name'][0]
            }
        })
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'error': 'Пользователь уже существует'})
    finally:
        conn.close()

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id, email, name, avatar FROM users 
    WHERE email = ? AND password = ?
    ''', (data['email'], data['password']))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user['id']
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'avatar': user['avatar']
            }
        })
    
    return jsonify({'success': False, 'error': 'Неверные данные'})

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True})

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, name, avatar FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return jsonify({
                'success': True,
                'user': dict(user)
            })
    
    return jsonify({'success': False, 'user': None})

# ========== РЕЦЕПТЫ ==========
@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT * FROM recipes ORDER BY created_at DESC
    ''')
    
    recipes = []
    for row in cursor.fetchall():
        recipe = dict(row)
        # Преобразуем JSON поля
        for field in ['ingredients', 'steps', 'tags']:
            if recipe[field]:
                recipe[field] = json.loads(recipe[field])
            else:
                recipe[field] = []
        recipes.append(recipe)
    
    conn.close()
    return jsonify({'success': True, 'recipes': recipes})

@app.route('/api/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,))
    row = cursor.fetchone()
    
    if row:
        recipe = dict(row)
        for field in ['ingredients', 'steps', 'tags']:
            if recipe[field]:
                recipe[field] = json.loads(recipe[field])
            else:
                recipe[field] = []
        
        # Увеличиваем просмотры
        cursor.execute('UPDATE recipes SET views = views + 1 WHERE id = ?', (recipe_id,))
        conn.commit()
        
        conn.close()
        return jsonify({'success': True, 'recipe': recipe})
    
    conn.close()
    return jsonify({'success': False, 'error': 'Рецепт не найден'})

@app.route('/api/recipes', methods=['POST'])
def create_recipe():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Требуется авторизация'})
    
    data = request.json
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Получаем имя пользователя
    cursor.execute('SELECT name FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    author_name = user['name'] if user else 'Неизвестный'
    
    try:
        cursor.execute('''
        INSERT INTO recipes (
            title, description, category, prep_time, cook_time, total_time,
            difficulty, servings, author_id, author_name, image_url,
            ingredients, steps, tags
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['title'],
            data.get('description', ''),
            data['category'],
            data.get('prep_time', 0),
            data.get('cook_time', 0),
            data.get('prep_time', 0) + data.get('cook_time', 0),
            data['difficulty'],
            data['servings'],
            user_id,
            author_name,
            data.get('image_url', ''),
            json.dumps(data.get('ingredients', [])),
            json.dumps(data.get('steps', [])),
            json.dumps(data.get('tags', []))
        ))
        
        recipe_id = cursor.lastrowid
        conn.commit()
        
        return jsonify({'success': True, 'recipe_id': recipe_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()

# ========== КАТЕГОРИИ ==========
@app.route('/api/categories', methods=['GET'])
def get_categories():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM categories ORDER BY name')
    categories = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'success': True, 'categories': categories})

# ========== ИЗБРАННОЕ ==========
@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Требуется авторизация'})
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT r.* FROM recipes r
    JOIN favorites f ON r.id = f.recipe_id
    WHERE f.user_id = ?
    ORDER BY f.created_at DESC
    ''', (user_id,))
    
    recipes = []
    for row in cursor.fetchall():
        recipe = dict(row)
        for field in ['ingredients', 'steps', 'tags']:
            if recipe[field]:
                recipe[field] = json.loads(recipe[field])
            else:
                recipe[field] = []
        recipes.append(recipe)
    
    conn.close()
    return jsonify({'success': True, 'recipes': recipes})

@app.route('/api/favorites/<int:recipe_id>', methods=['POST'])
def toggle_favorite(recipe_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Требуется авторизация'})
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Проверяем, есть ли уже в избранном
    cursor.execute('SELECT id FROM favorites WHERE user_id = ? AND recipe_id = ?', 
                  (user_id, recipe_id))
    existing = cursor.fetchone()
    
    try:
        if existing:
            # Удаляем
            cursor.execute('DELETE FROM favorites WHERE id = ?', (existing['id'],))
            added = False
        else:
            # Добавляем
            cursor.execute('INSERT INTO favorites (user_id, recipe_id) VALUES (?, ?)', 
                          (user_id, recipe_id))
            added = True
        
        conn.commit()
        return jsonify({'success': True, 'added': added})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()

@app.route('/api/favorites/<int:recipe_id>/check', methods=['GET'])
def check_favorite(recipe_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': True, 'is_favorite': False})
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM favorites WHERE user_id = ? AND recipe_id = ?', 
                  (user_id, recipe_id))
    result = cursor.fetchone()
    conn.close()
    
    return jsonify({'success': True, 'is_favorite': result is not None})

# ========== ПОИСК ==========
@app.route('/api/recipes/search', methods=['GET'])
def search_recipes():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'success': True, 'recipes': []})
    
    conn = get_db()
    cursor = conn.cursor()
    
    search_term = f"%{query}%"
    cursor.execute('''
    SELECT * FROM recipes 
    WHERE title LIKE ? OR description LIKE ? OR category LIKE ?
    ORDER BY created_at DESC
    ''', (search_term, search_term, search_term))
    
    recipes = []
    for row in cursor.fetchall():
        recipe = dict(row)
        for field in ['ingredients', 'steps', 'tags']:
            if recipe[field]:
                recipe[field] = json.loads(recipe[field])
            else:
                recipe[field] = []
        recipes.append(recipe)
    
    conn.close()
    return jsonify({'success': True, 'recipes': recipes})

# ========== СТАТИСТИКА ==========
@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM recipes')
    total_recipes = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM categories')
    total_categories = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM favorites')
    total_favorites = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'success': True,
        'stats': {
            'total_recipes': total_recipes,
            'total_users': total_users,
            'total_categories': total_categories,
            'total_favorites': total_favorites
        }
    })

# ========== МОИ РЕЦЕПТЫ ==========
@app.route('/api/recipes/my', methods=['GET'])
def get_my_recipes():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Требуется авторизация'})
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM recipes WHERE author_id = ? ORDER BY created_at DESC', 
                  (user_id,))
    
    recipes = []
    for row in cursor.fetchall():
        recipe = dict(row)
        for field in ['ingredients', 'steps', 'tags']:
            if recipe[field]:
                recipe[field] = json.loads(recipe[field])
            else:
                recipe[field] = []
        recipes.append(recipe)
    
    conn.close()
    return jsonify({'success': True, 'recipes': recipes})

# ========== АВТОРЫ ==========
@app.route('/api/authors', methods=['GET'])
def get_authors():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT u.id, u.name, u.email, u.avatar,
           COUNT(r.id) as recipes_count
    FROM users u
    LEFT JOIN recipes r ON u.id = r.author_id
    GROUP BY u.id
    HAVING recipes_count > 0
    ORDER BY recipes_count DESC
    ''')
    
    authors = []
    for row in cursor.fetchall():
        author = dict(row)
        authors.append(author)
    
    conn.close()
    return jsonify({'success': True, 'authors': authors})

