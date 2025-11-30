from django.contrib import admin
from .models import Category, Location, Post, Comment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published')
    list_editable = ('is_published',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published')
    list_editable = ('is_published',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'is_published', 
        'pub_date', 
        'author', 
        'category', 
        'price',
        'condition'
    )
    list_editable = ('is_published', 'category')
    search_fields = ('title', 'text', 'book_author')
    list_filter = ('category', 'location', 'condition')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')
