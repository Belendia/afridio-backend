from django.shortcuts import render
from core.models import Media


def media_list(request):
    context = {
        'medias': Media.objects.all()
    }
    return render(request, 'home.html', context)


def order_summary(request):
    return render(request, 'order_summary.html')
