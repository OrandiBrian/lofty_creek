from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ContactMessage, BlogPost, GalleryPhoto

def index(request):
    return render(request, 'public/index.html')

def about(request):
    return render(request, 'public/about.html')

def academics(request):
    return render(request, 'public/academics.html')

def admissions(request):
    return render(request, 'public/admissions.html')

def gallery(request):
    photos = GalleryPhoto.objects.filter(visible=True)
    categories = ['Campus', 'Academics', 'Events', 'Sports']
    return render(request, 'public/gallery.html', {'photos': photos, 'categories': categories})

def contact(request):
    if request.method == 'POST':
        from django.http import JsonResponse
        try:
            ContactMessage.objects.create(
                first_name=request.POST.get('first_name', ''),
                last_name=request.POST.get('last_name', ''),
                email=request.POST.get('email', ''),
                phone_number=request.POST.get('phone_number', ''),
                subject=request.POST.get('subject', ''),
                message=request.POST.get('message', '')
            )
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return render(request, 'public/contact.html')

def resources(request):
    posts = BlogPost.objects.filter(published=True)
    return render(request, 'public/resources.html', {'posts': posts})


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, published=True)
    recent = BlogPost.objects.filter(published=True).exclude(pk=post.pk)[:3]
    return render(request, 'public/blog_detail.html', {'post': post, 'recent': recent})

def events(request):
    return render(request, 'public/events.html')
