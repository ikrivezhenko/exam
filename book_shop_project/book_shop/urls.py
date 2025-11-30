from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView 

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'
handler403 = 'pages.views.permission_denied'

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('auth/', include('django.contrib.auth.urls')),
    
    path('', include('books.urls', namespace='books')),

    path('auth/logout/', LogoutView.as_view(http_method_names = ['get', 'post', 'options']), name='logout'),
    
    path('pages/', include('pages.urls', namespace='pages')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
