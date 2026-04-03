from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Player
from .forms import PlayerForm

class PlayerListView(ListView):
    model = Player
    template_name = 'players/player_list.html'

class PlayerCreateView(CreateView):
    model = Player
    form_class = PlayerForm
    template_name = 'players/player_form.html'
    success_url = reverse_lazy('player_list')

class PlayerUpdateView(UpdateView):
    model = Player
    form_class = PlayerForm
    template_name = 'players/player_form.html'
    success_url = reverse_lazy('player_list')

class PlayerDeleteView(DeleteView):
    model = Player
    template_name = 'players/player_confirm_delete.html'
    success_url = reverse_lazy('player_list')