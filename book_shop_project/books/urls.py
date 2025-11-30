from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.index, name='index'),
    path('auth/registration/', views.RegistrationView.as_view(), name='registration'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/create/', views.post_create, name='post_create'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='post_delete'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('category/<slug:category_slug>/', views.category_posts, name='category_posts'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('edit_profile/', views.profile_edit, name='profile_edit'),
]
