from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class PublishedModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True 

class Location(PublishedModel):
    name = models.CharField(max_length=256, verbose_name='Название места')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name

class Category(PublishedModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.title

class Post(PublishedModel):
    CONDITION_CHOICES = (
        ('new', 'Новая'),
        ('used', 'Б/У'),
        ('bad', 'Поврежденная'),
    )
    title = models.CharField(max_length=256, verbose_name='Название книги')
    text = models.TextField(verbose_name='Описание объявления')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена', default=0)
    book_author = models.CharField(max_length=256, verbose_name='Автор книги')
    condition = models.CharField(
        max_length=10, 
        choices=CONDITION_CHOICES, 
        default='used', 
        verbose_name='Состояние'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату в будущем, книга станет видна на сайте только в этот момент.'
    )
    image = models.ImageField(
        upload_to='book_images/', 
        verbose_name='Фото книги', 
        blank=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор объявления',
        related_name='posts' 
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True, 
        verbose_name='Местоположение',
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Жанр',
        related_name='posts'
    )
    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',) 
    def __str__(self):
        return self.title

class Comment(models.Model):
    text = models.TextField('Текст комментария')
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='comments',
        verbose_name='Автор'
    )
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='comments',
        verbose_name='Книга'
    )
    class Meta:
        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
    def __str__(self):
        return f'Комментарий пользователя {self.author} к {self.post}'[:30]
