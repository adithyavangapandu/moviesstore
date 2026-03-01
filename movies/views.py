from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Movie, Review
from accounts.models import Profile
from cart.models import Item, Order
from django.db.models import Sum, Count
from accounts.forms import regions
from django.contrib.auth.decorators import login_required
# Create your views here.


def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html',
                  {'template_data': template_data})


def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie, is_hidden=False)
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html',
                  {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment']!= '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',
            {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id,
        user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def create_report(request, movie_id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user == review.user:
        return redirect('movies.show', id=movie_id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Report Review'
        template_data['review'] = review
        return render(request, 'movies/create_report.html',
            {'template_data': template_data})
    if request.method == 'POST' and request.POST['reason']!= '':
        review = Review.objects.get(id=review_id)
        review.is_hidden = True
        review.report_reason = request.POST['reason']
        review.save()
        return redirect('movies.show', id=movie_id)
    else:
        return redirect('movies.show', id=movie_id)

@login_required
def local_popularity_filter_data(request):
    get_region = request.GET.get('region')
    get_state = request.GET.get('state')
    get_city = request.GET.get('city')

    all_profiles = Profile.objects.all()
    if get_region: all_profiles = all_profiles.filter(region=get_region)
    if get_state: all_profiles = all_profiles.filter(state=get_state)
    if get_city: all_profiles = all_profiles.filter(city=get_city)

    cities = list(all_profiles.values_list('city', flat=True).distinct())
    states = list(all_profiles.values_list('state', flat=True).distinct())
    regions = list(all_profiles.values_list('region', flat=True).distinct())

    markers = []
    for profile in all_profiles:
        markers.append({
                "lat": profile.latitude,
                "lon": profile.longitude,
                "username": profile.user.username,
                'is_current_user': profile.user_id == request.user.id,
                'city': profile.city,
                'state': profile.state,
                'region': profile.region,
            })

    user_ids = list(all_profiles.values_list("user_id", flat=True))

    movie_rows = (
        Item.objects
        .filter(order__user_id__in=user_ids)
        .values("movie_id", "movie__name")
        .annotate(
            total_units=Sum("quantity"),
            num_orders=Count("order_id", distinct=True),
        )
        .order_by("-total_units", "-num_orders", "movie__name")
    )
    TOP_K = 5
    movies = [
        {
            "movie_id": row["movie_id"],
            "movie_name": row["movie__name"],
            "total_units": row["total_units"],
            "num_orders": row["num_orders"],
        }
        for row in movie_rows[:TOP_K]
    ]
    return JsonResponse({
        "markers": markers,
        "options": {
            "cities": cities,
            "states": states,
            "regions": regions,
        },
        "movies": movies,
    })


@login_required
def popularity_map(request):


    return render(request, 'movies/popularity_map.html',)

'''
3 layers of filters. Region, state, city.
Do region or/and state, then unlock city.
?region=SOUTH
'''