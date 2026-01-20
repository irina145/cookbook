from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm

def register_view(request):
    """Регистрация пользователя"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    """Вход пользователя"""
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Редирект на следующую страницу или главную
            next_page = request.GET.get('next', 'home')
            return redirect(next_page)
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    """Выход пользователя"""
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('home')

@login_required
def profile_view(request):
    """Профиль пользователя"""
    user = request.user
    user_recipes = user.recipes.all()
    
    user_comments = user.comments.count()
    
    context = {
        'user': user,
        'recipes_count': user_recipes.count(),
        
        'comments_count': user_comments,
        'user_recipes': user_recipes[:5],  # Последние 5 рецептов
    }
    return render(request, 'accounts/profile.html', context)