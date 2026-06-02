from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def result(request):
    return render(request, 'resultpage.html')