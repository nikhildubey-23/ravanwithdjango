from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('view_history/', views.view_history_page, name='view_history'),
    path('clear_history/', views.clear, name='clear_history'),
    path('about/', views.about, name='about'),
    path('reachout/', views.reachout, name='reachout'),
]