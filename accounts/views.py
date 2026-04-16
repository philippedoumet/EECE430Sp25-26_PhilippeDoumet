from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views import View


class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return self._redirect_by_role(request.user)
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return self._redirect_by_role(user)
        return render(request, self.template_name, {'error': 'Invalid username or password.'})

    def _redirect_by_role(self, user):
        if user.is_superuser or user.groups.filter(name='Owner').exists():
            return redirect('owner_dashboard')
        if user.groups.filter(name='Coach').exists():
            return redirect('coach_dashboard')
        if user.groups.filter(name='Player').exists():
            return redirect('player_dashboard')
        return render(self.request, self.template_name, {'error': 'Your account has no portal assigned.'})


def logout_view(request):
    logout(request)
    return redirect('login')
