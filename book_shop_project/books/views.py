from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .models import Post, Category, User, Comment
from .forms import PostForm, CommentForm, UserRegistrationForm, UserEditForm

def get_page_obj(request, queryset):
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

def get_published_posts_queryset():
    now = timezone.now()
    return Post.objects.select_related(
        'author', 'location', 'category'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=now
    )

def index(request):
    all_posts = Post.objects.all()
    print(f"Всего постов в базе: {all_posts.count()}")
    for post in all_posts:
        print(f"Книга: {post.title}")
        print(f" - is_published: {post.is_published}")
        print(f" - pub_date: {post.pub_date} (Текущее время сервера: {timezone.now()})")
        print(f" - category: {post.category} (Опубликована: {post.category.is_published if post.category else 'Нет категории'})")
    post_list = get_published_posts_queryset()
    print(f"Постов после фильтрации: {post_list.count()}")
    page_obj = get_page_obj(request, post_list)
    context = {'page_obj': page_obj}
    return render(request, 'books/index.html', context)

def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        now = timezone.now()
        if (not post.is_published or 
            not post.category.is_published or 
            post.pub_date > now):
            pass
    form = CommentForm()
    context = {'post': post, 'form': form}
    return render(request, 'books/post_detail.html', context)

def category_posts(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, is_published=True)
    post_list = category.posts.select_related('author', 'location').filter(
        is_published=True, pub_date__lte=timezone.now()
    )
    page_obj = get_page_obj(request, post_list)
    context = {'category': category, 'page_obj': page_obj}
    return render(request, 'books/category.html', context)

def profile(request, username):
    author = get_object_or_404(User, username=username)
    if request.user == author:
        post_list = author.posts.all().select_related('category', 'location')
    else:
        post_list = author.posts.filter(
            is_published=True, category__is_published=True, pub_date__lte=timezone.now()
        ).select_related('category', 'location')
    page_obj = get_page_obj(request, post_list)
    context = {'profile': author, 'page_obj': page_obj}
    return render(request, 'books/profile.html', context)

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('books:profile', username=request.user.username)
    else:
        form = UserEditForm(instance=request.user)
    return render(request, 'books/user_form.html', {'form': form})

class RegistrationView(CreateView):
    template_name = 'registration/registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('books:index')

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('books:profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'books/create.html', {'form': form})

@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('books:post_detail', post_id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('books:post_detail', post_id=post_id)
    else:
        form = PostForm(instance=post)
    return render(request, 'books/create.html', {'form': form, 'is_edit': True})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('books:post_detail', post_id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('books:profile', username=request.user.username)
    return render(request, 'books/delete.html', {'object': post, 'type': 'post'})

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('books:post_detail', post_id=post_id)

@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect('books:post_detail', post_id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('books:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'books/comment.html', {'form': form, 'comment': comment})

@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect('books:post_detail', post_id=post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('books:post_detail', post_id=post_id)
    return render(request, 'books/delete.html', {'object': comment, 'type': 'comment'})
