# scores/urls.py（仮にこうなら）
from django.urls import path
from . import views

urlpatterns = [
    path('', views.score_list, name='score_list'),
    path('upload/', views.upload_scores, name='upload_scores'),
    path('scores/mensfinal/', views.mens_final, name='mens_final'),
    path('scores/womensfinal/', views.womens_final, name='womens_final'),
]