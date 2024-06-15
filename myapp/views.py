from django.shortcuts import render, redirect
from rest_framework import viewsets, permissions
from .models import Contact, UserStatus
from .forms import ContactForm, UserRegistrationForm
from .serializers import ContactSerializer
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.AllowAny]

def online_users(request):
    online_users = UserStatus.objects.filter(is_online=True)
    return render(request, 'OnlineUsers.html', {'online_users': online_users})

def user_authenticated(user):
    return user.is_authenticated

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def profile(request):
    return render(request, 'profile.html')

@login_required
@user_passes_test(user_authenticated, login_url='/register/')
def contacts(request):
    contacts = Contact.objects.all()
    return render(request, 'contacts.html', {'contacts': contacts})

@login_required
def add_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contacts')
    else:
        form = ContactForm()
    return render(request, 'add_contact.html', {'form': form})

@login_required
def edit_contact(request, contact_id):
    contact = Contact.objects.get(pk=contact_id)
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            return redirect('contacts')
    else:
        form = ContactForm(instance=contact)
    return render(request, 'edit_contact.html', {'form': form, 'contact': contact})

@login_required
def delete_contact(request, contact_id):
    contact = Contact.objects.get(pk=contact_id)
    if request.method == 'POST':
        contact.delete()
        return redirect('contacts')
    return render(request, 'delete_contact.html', {'contact': contact})

def logout_view(request):
    logout(request)
    return redirect('home')
