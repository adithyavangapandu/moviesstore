from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='home.index'),
    path('about', views.about, name='home.about'),
    path('admin-dashboard', views.admin_dashboard, name = 'home.admin-dashboard' ),
    path('admin-comments', views.admin_comments, name = 'home.admin-comments' )
]