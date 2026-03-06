from django.shortcuts import render, redirect
from cart.models import Item

# Create your views here.
def index(request):
    template_data = {}
    template_data['title'] = 'Movies Store'
    return render(request, 'home/index.html', {
        'template_data': template_data})

def about(request):
    template_data = {}
    template_data['title'] = 'About'
    return render(request,
                  'home/about.html',
                  {'template_data': template_data})

def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('home.index')
    template_data = {}
    template_data['title'] = 'Admin Dashboard'
    items = Item.objects.all()
    movie_counts = {}
    for item in items:
        name = item.movie.name
        if name in movie_counts:
            movie_counts[name] += item.quantity
        else:
            movie_counts[name] = item.quantity
    most_purchased = None
    if movie_counts:
        top_movie = max(movie_counts, key = movie_counts.get)
        most_purchased = { 'movie_name' : top_movie, 'total_purchased': movie_counts[top_movie]}
    template_data['most_purchased'] = most_purchased
    return render(request, 'home/admin_dashboard.html' , {'template_data': template_data})