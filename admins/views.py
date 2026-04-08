from django.shortcuts import render, redirect
from django.contrib import messages
from users.models import UserRegistrationModel


# Create your views here.

def AdminLoginCheck(request):
    if request.method == 'POST':
        usrid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        print("User ID is = ", usrid)
        if usrid == 'admin' and pswd == 'admin':
            return render(request, 'admins/AdminHome.html')
        elif usrid == 'Admin' and pswd == 'Admin':
            return render(request, 'admins/AdminHome.html')
        else:
            messages.success(request, 'Please Check Your Login Details')
    return render(request, 'AdminLogin.html', {})


def ViewRegisteredUsers(request):
    data = UserRegistrationModel.objects.all()
    return render(request, 'admins/RegisteredUsers.html', {'data': data})


def AdminActivaUsers(request):
    if request.method == 'GET':
        id = request.GET.get('uid')
        status = 'activated'
        print("PID = ", id, status)
        UserRegistrationModel.objects.filter(id=id).update(status=status)
        data = UserRegistrationModel.objects.all()
        return render(request, 'admins/RegisteredUsers.html', {'data': data})


def AdminDeleteUser(request):
    if request.method == 'GET':
        uid = request.GET.get('uid')
        UserRegistrationModel.objects.filter(id=uid).delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('ViewRegisteredUsers')


def AdminEditUser(request):
    uid = request.GET.get('uid')
    user = UserRegistrationModel.objects.get(id=uid)
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        locality = request.POST.get('locality')
        
        UserRegistrationModel.objects.filter(id=uid).update(
            name=name, email=email, mobile=mobile, locality=locality
        )
        messages.success(request, 'User updated successfully.')
        return redirect('ViewRegisteredUsers')
    
    return render(request, 'admins/EditUser.html', {'user': user})


def AdminHome(request):
    return render(request, 'admins/AdminHome.html')