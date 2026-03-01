from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='movies.index'),
    path('popularity-map/', views.popularity_map, name='movies.popularity_map'),
    path('local-popularity-map/data/', views.local_popularity_filter_data, name='local_popularity_filter_data'),
    path('<int:id>/', views.show, name='movies.show'),
    path('<int:id>/review/create/', views.create_review, name='movies.create_review'),
    path('<int:id>/review/<int:review_id>/edit/', views.edit_review, name='movies.edit_review'),
    path('<int:id>/review/<int:review_id>/delete/', views.delete_review, name='movies.delete_review'),
    path('<int:movie_id>/review/<int:review_id>/report/', views.create_report, name='movies.create_report'),
]