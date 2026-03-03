from django.shortcuts import render

def index(request):
    return render(request, 'public/index.html')

def about(request):
    return render(request, 'public/about.html')

def academics(request):
    return render(request, 'public/academics.html')

def admissions(request):
    return render(request, 'public/admissions.html')

def gallery(request):
    return render(request, 'public/gallery.html')

def contact(request):
    return render(request, 'public/contact.html')

def resources(request):
    return render(request, 'public/resources.html')

def events(request):
    return render(request, 'public/events.html')
