from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('sessions/', views.session_list, name='session_list'),
    path('session/create/', views.session_create, name='session_create'),
    path('session/edit/<int:pk>/', views.session_edit, name='session_edit'),
    path('goal/', views.goal_view, name='goal_view'),
    path('import/', views.import_csv, name='import_csv'),
    path('export/', views.export_csv, name='export_csv'),
]