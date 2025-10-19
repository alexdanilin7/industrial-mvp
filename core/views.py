from django.shortcuts import render

# Create your views here.


from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import render
from .forms import CustomAuthenticationForm

class HTMXLoginView(LoginView):
    template_name = 'login_modal.html'
    form_class = CustomAuthenticationForm

    def form_invalid(self, form):
        """Вызывается при ошибке валидации"""
        # Возвращаем только контейнер формы с ошибками
        return render(self.request, 'login_form_partial.html', {'form': form})

    def form_valid(self, form):
        """Успешный вход — редирект на панель"""
        super().form_valid(form)
        return HttpResponse('<script>window.location.href="/admin-panel/";</script>')