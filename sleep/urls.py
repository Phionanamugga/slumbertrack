
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

# Create a router and register our ViewSets from api_views
router = DefaultRouter()
router.register(r'sleepsessions', api_views.SleepSessionViewSet, basename='sleepsession')
router.register(r'sleepgoals', api_views.SleepGoalViewSet, basename='sleepgoal')

app_name = 'sleep'

urlpatterns = [

    path('login/', views.login_view, name='login'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('sessions/', views.session_list, name='session_list'),
    path('session/create/', views.session_create, name='session_create'),
    path('session/edit/<int:pk>/', views.session_edit, name='session_edit'),
    path('goal/', views.goal_view, name='goal_view'),
    path('import/', views.import_csv, name='import_csv'),
    path('export/', views.export_csv, name='export_csv'),
   
    
    # API endpoints (use api_views.py)
    path('api/', include(router.urls)),
]
