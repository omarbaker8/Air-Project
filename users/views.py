from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.views.generic import DetailView
from .models import Profile
from django.contrib.auth.mixins import LoginRequiredMixin



# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully, now you can login.')
            return redirect('login') 
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})



class ProfileView(LoginRequiredMixin, DetailView):
    template_name = 'users/profile.html'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method != 'POST':
            context['u_form'] = UserUpdateForm(instance=self.request.user)
            context['p_form'] = ProfileUpdateForm(instance=self.request.user.profile)
        context['avatar_choices'] = Profile.AVATAR_CHOICES
        return context
    
    def post(self, request, *args, **kwargs):
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your account has been updated')
            return redirect('home')
        else:
            context = self.get_context_data()
            context['u_form'] = u_form
            context['p_form'] = p_form
            return self.render_to_response(context)

