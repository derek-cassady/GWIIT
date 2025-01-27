from django.shortcuts import render
from .models import Site  # Make sure you have a Site model in your app

def site_list(request):
    # Fetch all sites for listing
    sites = Site.objects.all()

    # Render the site list template
    return render(request, 'sites/site_list.html', {
        'sites': sites,
    })

def site_detail(request):
    # Fetch all sites for listing
    sites = Site.objects.all()

    # Render the site detail template
    return render(request, 'sites/site_detail.html', {
        'sites': sites,
    })