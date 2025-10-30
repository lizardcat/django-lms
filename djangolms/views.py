from django.shortcuts import render


def home_view(request):
    """
    Home page view.
    """
    return render(request, 'home.html')
