import sqlite3
import json
from datetime import datetime
import hashlib

def create_database():
    """Создание базы данных SQLite для кулинарной книги"""
    
    # Подключение к базе данных (файл будет создан автоматически)
    conn = sqlite3.connect('cookbook.db')
    cursor = conn.cursor()
    
    print("Создание базы данных...")
    
    # 1. Таблица пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        avatar TEXT,
        role TEXT DEFAULT 'Кулинарный энтузиаст',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 2. Таблица категорий
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        icon TEXT NOT NULL,
        description TEXT
    )
    ''')
    
    # 3. Таблица рецептов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        category_id INTEGER NOT NULL,
        author_id INTEGER NOT NULL,
        preparation_time INTEGER NOT NULL,
        servings INTEGER NOT NULL,
        difficulty TEXT NOT NULL,
        image_url TEXT,
        views INTEGER DEFAULT 0,
        average_rating REAL DEFAULT 0,
        rating_count INTEGER DEFAULT 0,
        tags TEXT DEFAULT '[]',  -- JSON массив
        ingredients TEXT DEFAULT '[]',  -- JSON массив
        steps TEXT DEFAULT '[]',  -- JSON массив
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories (id),
        FOREIGN KEY (author_id) REFERENCES users (id)
    )
    ''')
    
    # 4. Таблица избранного
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        recipe_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, recipe_id),
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (recipe_id) REFERENCES recipes (id)
    )
    ''')
    
    # 5. Таблица оценок
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        recipe_id INTEGER NOT NULL,
        value INTEGER NOT NULL CHECK (value >= 1 AND value <= 5),
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, recipe_id),
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (recipe_id) REFERENCES recipes (id)
    )
    ''')
    
    # 6. Таблица логов активности
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        details TEXT DEFAULT '{}',  -- JSON объект
        ip_address TEXT,
        user_agent TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    print("Таблицы созданы успешно!")
    
    # Добавление начальных данных
    add_initial_data(cursor)
    
    # Сохранение изменений и закрытие соединения
    conn.commit()
    conn.close()
    
    print("\n✅ База данных 'cookbook.db' успешно создана!")
    print("📍 Расположение: в той же папке, где находится этот скрипт")

def add_initial_data(cursor):
    """Добавление начальных данных в базу"""
    
    print("\nДобавление начальных данных...")
    
    # 1. Добавляем категории
    categories = [
        ('Супы', '🥣', 'Разнообразные первые блюда'),
        ('Основные блюда', '🍛', 'Сытные основные блюда'),
        ('Салаты', '🥗', 'Овощные и мясные салаты'),
        ('Десерты', '🍰', 'Сладкие угощения'),
        ('Выпечка', '🥐', 'Хлеб, булочки, пироги'),
        ('Закуски', '🍤', 'Легкие закуски'),
        ('Напитки', '🥤', 'Напитки и коктейли'),
        ('Завтраки', '🍳', 'Блюда для завтрака'),
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO categories (name, icon, description)
    VALUES (?, ?, ?)
    ''', categories)
    
    print(f"✅ Добавлено категорий: {len(categories)}")
    
    # 2. Добавляем тестовых пользователей
    users = [
        ('anna@mail.ru', 'anna123', 'Анна Иванова', 'АИ', 'Шеф-повар'),
        ('misha@mail.ru', 'misha123', 'Михаил Петров', 'МП', 'Кулинарный блогер'),
        ('elena@mail.ru', 'elena123', 'Елена Смирнова', 'ЕС', 'Кондитер'),
        ('alex@mail.ru', 'alex123', 'Алексей Козлов', 'АК', 'Бармен'),
        ('olga@mail.ru', 'olga123', 'Ольга Николаева', 'ОН', 'Диетолог'),
        ('dima@mail.ru', 'dima123', 'Дмитрий Соколов', 'ДС', 'Шеф-повар'),
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO users (email, password, name, avatar, role)
    VALUES (?, ?, ?, ?, ?)
    ''', users)
    
    print(f"✅ Добавлено пользователей: {len(users)}")
    
    # 3. Добавляем тестовые рецепты
    # Получаем ID категорий и пользователей
    cursor.execute("SELECT id, name FROM categories")
    categories_dict = {name: id for id, name in cursor.fetchall()}
    
    cursor.execute("SELECT id, email FROM users")
    users_dict = {email: id for id, email in cursor.fetchall()}
    
    recipes = [
        {
            'title': 'Классический борщ с говядиной',
            'description': 'Насыщенный, ароматный борщ с нежной говядиной и свеклой - классика русской кухни.',
            'category_id': categories_dict['Супы'],
            'author_id': users_dict['anna@mail.ru'],
            'preparation_time': 120,
            'servings': 6,
            'difficulty': 'Средняя',
            'image_url': 'https://img.freepik.com/premium-photo/chicken-soup-with-vegetables-wooden-table_135427-2442.jpg',
            'tags': json.dumps(['Русская кухня', 'С мясом', 'Свекла', 'Картофель', 'Овощи']),
            'ingredients': json.dumps([
                'Говядина (лопатка) - 500 г',
                'Свекла - 2 шт. средние',
                'Картофель - 3-4 шт.',
                'Морковь - 1 шт.',
                'Лук репчатый - 1 шт.',
                'Капуста белокочанная - 300 г',
                'Томатная паста - 2 ст. ложки',
                'Чеснок - 3 зубчика',
                'Сметана - для подачи',
                'Укроп свежий - пучок',
                'Лавровый лист - 2 шт.',
                'Соль, перец - по вкусу',
                'Масло растительное - 3 ст. ложки'
            ]),
            'steps': json.dumps([
                'Говядину промойте, нарежьте кубиками. Залейте холодной водой, доведите до кипения.',
                'Снимите пену, убавьте огонь и варите 1,5 часа до мягкости мяса.',
                'Пока варится мясо, подготовьте овощи. Свеклу и морковь натрите, лук нарежьте.',
                'Обжарьте лук и морковь, затем свеклу с томатной пастой.',
                'Добавьте овощи в бульон, варите до готовности.',
                'В конце добавьте чеснок, лавровый лист, соль и перец.',
                'Подавайте со сметаной и свежим укропом.'
            ])
        },
        {
            'title': 'Спагетти Карбонара',
            'description': 'Классические итальянские спагетти с беконом, яйцами и сыром пармезан.',
            'category_id': categories_dict['Основные блюда'],
            'author_id': users_dict['misha@mail.ru'],
            'preparation_time': 25,
            'servings': 3,
            'difficulty': 'Легкая',
            'image_url': 'https://img.freepik.com/premium-vector/plate-with-delicious-penne-pasta-sauce-white-background_906149-104329.jpg',
            'tags': json.dumps(['Итальянская кухня', 'С макаронами', 'Быстрое', 'С беконом', 'С сыром']),
            'ingredients': json.dumps([
                'Спагетти - 300 г',
                'Бекон - 150 г',
                'Яйца куриные - 3 шт.',
                'Желтки - 2 шт.',
                'Сыр пармезан - 80 г',
                'Чеснок - 2 зубчика',
                'Сливки 20% - 100 мл',
                'Соль, перец черный - по вкусу',
                'Оливковое масло - 2 ст. ложки'
            ]),
            'steps': json.dumps([
                'Отварите спагетти согласно инструкции.',
                'Обжарьте бекон до хрустящей корочки.',
                'Взбейте яйца, желтки и сливки. Добавьте тертый пармезан.',
                'Слейте воду со спагетти, оставив немного воды.',
                'Соедините горячие спагетти с беконом.',
                'Влейте яичную смесь, постоянно помешивая.',
                'Сразу подавайте с дополнительным пармезаном.'
            ])
        },
        {
            'title': 'Шоколадный торт',
            'description': 'Нежный шоколадный торт с кремом из темного шоколада.',
            'category_id': categories_dict['Десерты'],
            'author_id': users_dict['elena@mail.ru'],
            'preparation_time': 90,
            'servings': 8,
            'difficulty': 'Сложная',
            'image_url': 'https://img.freepik.com/free-photo/sweet-food-desserts-with-whipped-cream-generated-by-ai_188544-15728.jpg',
            'tags': json.dumps(['Десерт', 'Шоколад', 'Торт', 'Праздничное', 'Сложное']),
            'ingredients': json.dumps([
                'Мука пшеничная - 250 г',
                'Какао-порошок - 80 г',
                'Сахар - 300 г',
                'Яйца - 4 шт.',
                'Сливочное масло - 200 г',
                'Сметана - 200 г',
                'Разрыхлитель - 2 ч. ложки',
                'Темный шоколад - 200 г',
                'Сливки 33% - 300 мл'
            ]),
            'steps': json.dumps([
                'Смешайте сухие ингредиенты: муку, какао, разрыхлитель.',
                'Взбейте яйца с сахаром до пышной массы.',
                'Добавьте растопленное масло и сметану, перемешайте.',
                'Постепенно добавьте сухие ингредиенты.',
                'Выпекайте в разогретой до 180°C духовке 40-45 минут.',
                'Приготовьте крем: растопите шоколад со сливками.',
                'Промажьте торт остывшим кремом.',
                'Дайте торту пропитаться 4-6 часов.'
            ])
        }
    ]
    
    for recipe in recipes:
        cursor.execute('''
        INSERT OR IGNORE INTO recipes (
            title, description, category_id, author_id, preparation_time,
            servings, difficulty, image_url, tags, ingredients, steps
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            recipe['title'], recipe['description'], recipe['category_id'],
            recipe['author_id'], recipe['preparation_time'], recipe['servings'],
            recipe['difficulty'], recipe['image_url'], recipe['tags'],
            recipe['ingredients'], recipe['steps']
        ))
    
    print(f"✅ Добавлено рецептов: {len(recipes)}")
    
    # 4. Добавляем несколько оценок
    cursor.execute("SELECT id FROM recipes LIMIT 3")
    recipe_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM users LIMIT 3")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    ratings = []
    for i, recipe_id in enumerate(recipe_ids):
        ratings.append((user_ids[i % len(user_ids)], recipe_id, 5, 'Отличный рецепт!'))
    
    cursor.executemany('''
    INSERT OR IGNORE INTO ratings (user_id, recipe_id, value, comment)
    VALUES (?, ?, ?, ?)
    ''', ratings)
    
    print(f"✅ Добавлено оценок: {len(ratings)}")
    
    print("\n🎉 Начальные данные успешно добавлены!")

def check_database():
    """Проверка содержимого базы данных"""
    conn = sqlite3.connect('cookbook.db')
    cursor = conn.cursor()
    
    print("\n📊 Проверка содержимого базы данных:")
    
    tables = ['users', 'categories', 'recipes', 'favorites', 'ratings', 'activity_logs']
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} записей")
    
    conn.close()

if __name__ == '__main__':
    print("=" * 50)
    print(" СОЗДАНИЕ БАЗЫ ДАННЫХ КУЛИНАРНОЙ КНИГИ")
    print("=" * 50)
    
    try:
        create_database()
        check_database()
        
        print("\n" + "=" * 50)
        print("🎯 База данных готова к использованию!")
        print("=" * 50)
        print("\nСтруктура базы данных:")
        print("1. users - Пользователи")
        print("2. categories - Категории рецептов")
        print("3. recipes - Рецепты")
        print("4. favorites - Избранное")
        print("5. ratings - Оценки")
        print("6. activity_logs - Логи активности")
        
        print("\n🧪 Тестовые пользователи:")
        print("  anna@mail.ru / anna123 - Анна Иванова")
        print("  misha@mail.ru / misha123 - Михаил Петров")
        print("  elena@mail.ru / elena123 - Елена Смирнова")
        
    except Exception as e:
        print(f"\n❌ Ошибка при создании базы данных: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nНажмите Enter для выхода...")
