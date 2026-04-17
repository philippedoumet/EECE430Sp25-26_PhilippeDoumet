from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views import View


def _no_superuser():
    """Return True when the database has no superuser yet."""
    return not User.objects.filter(is_superuser=True).exists()


class SetupView(View):
    """First-run wizard: create the initial superuser account."""
    template_name = 'accounts/setup.html'

    def get(self, request):
        if not _no_superuser():
            return redirect('login')
        return render(request, self.template_name)

    def post(self, request):
        if not _no_superuser():
            return redirect('login')

        username = request.POST.get('username', '').strip()
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm  = request.POST.get('confirm_password', '')

        errors = []
        if not username:
            errors.append('Username is required.')
        elif User.objects.filter(username=username).exists():
            errors.append('That username is already taken.')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')

        if errors:
            return render(request, self.template_name, {'errors': errors,
                                                        'username': username,
                                                        'email': email})

        User.objects.create_superuser(username=username, email=email, password=password)
        return redirect('setup_done')


class SetupDoneView(View):
    template_name = 'accounts/setup_done.html'

    def get(self, request):
        return render(request, self.template_name)


class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        # Redirect to first-run wizard if no superuser exists yet
        if _no_superuser():
            return redirect('setup')
        if request.user.is_authenticated:
            return self._redirect_by_role(request.user)
        return render(request, self.template_name)

    def post(self, request):
        if _no_superuser():
            return redirect('setup')

        username      = request.POST.get('username', '').strip()
        password      = request.POST.get('password', '')
        selected_role = request.POST.get('role', 'owner')   # owner | coach | player

        user = authenticate(request, username=username, password=password)
        if not user:
            return render(request, self.template_name, {
                'error': 'Invalid username or password.',
                'selected_role': selected_role,
                'username': username,
            })

        # Validate that the user actually belongs to the selected role
        role_ok = {
            'owner':  user.is_superuser or user.groups.filter(name='Owner').exists(),
            'coach':  user.groups.filter(name='Coach').exists(),
            'player': user.groups.filter(name='Player').exists(),
        }
        if not role_ok.get(selected_role, False):
            actual = self._actual_role_label(user)
            return render(request, self.template_name, {
                'error': (
                    f'This account is not registered as a {selected_role.capitalize()}. '
                    f'{"Try signing in as " + actual + "." if actual else "Ask the admin to assign you a role."}'
                ),
                'selected_role': selected_role,
                'username': username,
            })

        login(request, user)
        return self._redirect_by_role(user)

    def _actual_role_label(self, user):
        if user.is_superuser or user.groups.filter(name='Owner').exists():
            return 'Owner'
        if user.groups.filter(name='Coach').exists():
            return 'Coach'
        if user.groups.filter(name='Player').exists():
            return 'Player'
        return ''

    def _redirect_by_role(self, user):
        if user.is_superuser or user.groups.filter(name='Owner').exists():
            return redirect('owner_dashboard')
        if user.groups.filter(name='Coach').exists():
            return redirect('coach_dashboard')
        if user.groups.filter(name='Player').exists():
            return redirect('player_dashboard')
        return render(self.request, self.template_name,
                      {'error': 'Your account has no portal assigned. Ask the admin to assign you a role.'})


def logout_view(request):
    logout(request)
    return redirect('login')
