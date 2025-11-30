from django.views.generic import TemplateView

def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)

def server_error(request):
    return render(request, 'pages/500.html', status=500)

def permission_denied(request, exception):
    return render(request, 'pages/403.html', status=403)

class AboutView(TemplateView):
    template_name = 'pages/about.html'

class RulesView(TemplateView):
    template_name = 'pages/rules.html'
