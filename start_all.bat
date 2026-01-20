@echo off
title Проверка и исправление CookBook
cd C:\Users\студент\Desktop\CookBook

echo ========================================
echo         ПРОВЕРКА ПРОЕКТА
echo ========================================
echo.

echo 1. Активируем виртуальное окружение...
call venv\Scripts\activate

echo 2. Проверяем установленные пакеты...
pip list | findstr Django
echo.

echo 3. Создаем миграции...
python manage.py makemigrations
echo.

echo 4. Применяем миграции...
python manage.py migrate

echo ========================================
echo         ЗАПУСК СЕРВЕРА
echo ========================================
echo.
echo 🌐 ОТКРОЙТЕ В БРАУЗЕРЕ:
echo 📍 http://localhost:8000/
echo 📍 http://localhost:8000/admin/
echo 📍 http://localhost:8000/api/recipes/
echo.
echo 🔑 Логин: admin
echo 🔑 Пароль: admin123
echo ========================================
echo.

python manage.py runserver
pause