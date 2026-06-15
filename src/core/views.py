from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, "home.html")

def ping(request):
    return render(request, "partials/ping.html")
