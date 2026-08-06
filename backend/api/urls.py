from django.urls import path

from . import views

urlpatterns = [
    path('auth/register/', views.register_view, name='auth-register'),
    path('auth/login/', views.login_view, name='auth-login'),
    path('auth/logout/', views.logout_view, name='auth-logout'),
    path('auth/telegram/', views.telegram_auth_view, name='auth-telegram'),
    path('auth/me/', views.me_view, name='auth-me'),
    path('auth/csrf/', views.csrf_view, name='auth-csrf'),

    path('categories/', views.categories_view, name='categories'),
    path('work-items/', views.work_items_view, name='work-items'),
    path('estimates/', views.estimates_view, name='estimates'),
    path('estimates/<int:pk>/', views.estimate_detail_view, name='estimate-detail'),
    path('estimates/<int:estimate_pk>/lines/', views.estimate_lines_view, name='estimate-lines'),
]
