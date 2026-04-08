from django.shortcuts import render, redirect
from users.forms import UserRegistrationForm

# Create your views here.
def index(request):
    return render(request, 'index.html', {})


def logout(request):
    request.session.flush()
    return redirect('index')

def UserLogin(request):
    return render(request, 'UserLogin.html', {})



def UserRegister(request):
    form = UserRegistrationForm()
    return render(request, 'UserRegistrations.html', {'form': form})

def AdminLogin(request):
    return render(request, 'AdminLogin.html', {})