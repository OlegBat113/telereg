from django.shortcuts import render

# Create your views here.

def index(request):
    context = {
        'products': ['Товар 1', 'Товар 2', 'Товар 3'],
    }
    return render(request, 'teleregapp/index.html', context)
