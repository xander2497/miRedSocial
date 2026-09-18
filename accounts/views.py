from django.shortcuts import render

# Create your views here.
def login_page(request):
    return render(request,'accounts/login.html')

def profile_page(request):
    return render(request,'accounts/profile.html')

def register_page(request):
    return render(request,'accounts/register.html')

def edit_profile_page(request):
    return render(request,'accounts/edit_profile.html')