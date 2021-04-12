from django.shortcuts import render,redirect

def error403(request):
    return render(request,'errors/403.html')

def error500(request):
    return render(request,'errors/500.html')

def error404(request):
    return render(request,'errors/404.html')