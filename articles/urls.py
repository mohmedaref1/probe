
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.article_list, name='article_list'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('publish/', views.article_create, name='article_create'),
    path('edit/<slug:slug>/', views.article_edit, name='article_edit'),
    path('delete/<slug:slug>/', views.article_delete, name='article_delete'),
    path('published/', views.article_admin_list, name='article_admin_list'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(next_page='/'), name='logout'),
    path('profile/', views.user_profile, name='user_profile'),
    
    # Language and theme toggle endpoints
    path('set-language/<str:language>/', views.set_language, name='set_language'),
    path('set-theme/', views.set_theme, name='set_theme'),
    path('update-article-state/', views.update_article_state, name='update_article_state'),
    
    # Image upload endpoints
    path('upload-image/', views.upload_image, name='upload_image'),
    path('delete-image/', views.delete_image, name='delete_image'),
]
