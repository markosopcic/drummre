from django.contrib.auth import login, authenticate
from django.http import HttpResponseBadRequest,HttpResponseRedirect
from django.shortcuts import render
import json
import math
from django.shortcuts import get_object_or_404
import requests
from collections import Counter
from django.http import HttpResponse
from django.urls import reverse
from django.core import serializers
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth.decorators import login_required
import urllib3
import random
from django.contrib import messages
from django.http import JsonResponse
import re
import pymongo
from pymongo import MongoClient
client = MongoClient('localhost', 27017)

def userPreferences(request):
    genres = Movie.objects.mongo_distinct("genres")
    context = {'genres': genres}
    return render(request, 'shows/preferences.html', context)

def movieDetail(request, id):
    movie = get_object_or_404(Movie, id=id)

    tmdb_url1 = 'https://api.themoviedb.org/3/movie/'
    tmdb_url2 = '/recommendations?api_key=a87b7455c36d6c15b40a0d194a6dd771&language=en-US&page=1'
    tmdb_list = []

    movie_res = requests.get(tmdb_url1 + str(id) + tmdb_url2)
    if movie_res.status_code == 200:
        movie_json = json.loads(movie_res.text)
        if movie_json.get('total_results') != 0:
            for obj in movie_json.get('results'):
                tmdb_list.append(obj.get('id'))

    recommendedMovies = Movie.objects.filter(id__in=tmdb_list)
    reviews = Review.objects.filter(id=id)
    if reviews.exists():
        reviews = reviews.first().results
    else:
        reviews = None
    context = {'movie': movie, 'recommended': recommendedMovies,"reviews":reviews}
    return render(request, 'shows/detailMovie.html', context)


def recommendMovies(request):
    if request.user.is_authenticated is False:
        return render(request, "some.html", {"movies": []})
    liked = UserLikedMovies.objects.filter(id=request.user.id)
    if not liked.exists():
        return render(request,"some.html",{"movies":[]})
    liked = liked.first().liked_movies
    tmdb_ids = Movie.objects.mongo_find({"imdb_id":{"$in":liked}}).distinct("id")
    movie_names = ['Toy Story 2', 'Life Itself']

    td_url = 'https://tastedive.com/api/similar?k=353012-Drumre-AR4Y3PKE&q=movie:'
    tmdb_url1 = 'https://api.themoviedb.org/3/movie/'
    tmdb_url2 = '/recommendations?api_key=a87b7455c36d6c15b40a0d194a6dd771&language=en-US&page=1'

    tmdb_list = []
    final_list = []

    skipped1 = 0
    skipped2 = 0

    # TASTEDIVE
    for name in movie_names:

        td_list = []
        movie_res = requests.get(td_url + str(name.strip()))
        if movie_res.status_code != 200:
            skipped1 += 1
            continue

        movie_json = json.loads(movie_res.text)

        if movie_json.get('Similar') is None:
            skipped1 += 1
            continue

        for obj in movie_json.get('Similar').get('Results'):
            if obj.get('Name') not in movie_names and obj.get('Type') == 'movie':
                td_list.append(obj.get('Name'))

        td_to_tmdb = Movie.objects.filter(title__in=td_list).values_list("id", flat=True)
        for obj in td_to_tmdb:
            tmdb_list.append(obj)

    print("Movies fetched (skipped: " + str(skipped1) + ")")

    # TMDB
    for id in tmdb_ids:

        movie_res = requests.get(tmdb_url1 + str(id) + tmdb_url2)
        if movie_res.status_code != 200:
            skipped2 += 1
            continue

        movie_json = json.loads(movie_res.text)

        if movie_json.get('total_results') == 0:
            skipped2 += 1
            continue

        for obj in movie_json.get('results'):
            if obj.get('id') not in tmdb_ids:
                tmdb_list.append(obj.get('id'))

    print("Movies fetched (skipped: " + str(skipped2) + ")")

    final_counter = Counter(tmdb_list)

    # u most common se napise broj filmova
    for obj in final_counter.most_common():
        print(obj)
        final_list.append(obj[0])

    resultMovies = list(Movie.objects.mongo_find({"id":{"$in":final_list}}))
    context = {'movies': resultMovies[:20]}
    return render(request, 'shows/recommend.html', context)

def listuserliked(request):
    if request.user.is_authenticated is False:
        return HttpResponseBadRequest()
    user_id = request.user.id
    res =  UserLikedMovies.objects.filter(id=user_id)
    if not res.exists():
        UserLikedMovies.objects.create(id=user_id,liked_movies=[])
        return render(request,'some.html',{})
    res = res[0].liked_movies
    movies = list(Movie.objects.mongo_find({"imdb_id":{"$all":res}}))
    return render(request,'some.html',{"movies":movies})

def popularMovies(request):
    itemsPerPage = 20
    year = request.GET.get('year')
    genre = request.GET.get('genre')

    filterDict = {}
    if genre:
        filterDict.update({"genres": {"$all": [re.compile(genre, re.IGNORECASE)]}})
    if year:
        regx = re.compile("^" + year, re.IGNORECASE)
        filterDict.update({"release_date": regx})

    page = request.GET.get("page")
    if not page:
        page = 1
    else:
        page = int(page)
    numOfPages = math.ceil(Movie.objects.mongo_find(filterDict).count() / itemsPerPage)
    paginator = {
        "page": page,
        "hasNext": True if page < numOfPages else False,
        "totalPages": numOfPages
    }

    movies = Movie.objects.mongo_find(filterDict).sort('popularity', pymongo.DESCENDING).skip(
        (page - 1) * itemsPerPage).limit(itemsPerPage)
    movies = list(movies)
    context = {'movies': movies, 'paginator': paginator}
    return render(request, 'shows/popular.html', context)

def likemovie(request):
    if request.user.is_authenticated:
        movie_id =request.GET.get("movie_id")
        user = UserLikedMovies.objects.filter(id=request.user.id)
        if user.exists() is False:
            UserLikedMovies.objects.create(id=request.user.id,liked_movies=[])
        user = UserLikedMovies.objects.filter(id = request.user.id).first()
        user.liked_movies.append(movie_id)
        UserLikedMovies.objects.filter(id = request.user.id).update(liked_movies=user.liked_movies)
        return HttpResponse(status=200)
    return HttpResponseBadRequest()

def signup(request):
    if request.method == 'POST':
        message = ""
        if len(request.POST.get("username")) == 0:
            message+="Username not set!\n"
        if len(request.POST.get("password")) < 8:
            message+="Password needs to be at least 8 characters long!\n"
        if request.POST.get("password") != request.POST.get("password2"):
            message+="Passwords do not match!\n"
        if len(request.POST.get("firstname")) == 0:
            message+="First Name is not set!\n"
        if len(request.POST.get("lastname")) == 0:
            message+="Last Name is not set!\n"
        if len(request.POST.get("email")) == 0:
            message+="Email not set!\n"
        if len(User.objects.filter(username=request.POST.get("username"))) > 0:
            message+="Username already taken!"
        if len(message)>0:
            messages.add_message(request,messages.INFO,message)
            return HttpResponseRedirect(reverse('index'))
        u = User.objects.create(username=request.POST.get("username"),first_name=request.POST.get("firstname"),last_name=request.POST.get("lastname"),email=request.POST.get("email"))
        u.set_password(request.POST.get("password"))
        u.save()
        user = authenticate(username=request.POST.get("username"), password=request.POST.get("password"))
        login(request, user)
        return render(request,'index.html')
    else:
        return render(request,'index.html')

def user_login(request):
    if request.method == 'POST':
        if request.path.count("login")>1:
            request.path = '/login'
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request,user)
                return render(request,'index.html',{})
            else:
                messages.add_message(request,messages.INFO,"Inactive account.")
                return HttpResponseRedirect(reverse('index'))
        else:
            messages.add_message(request,messages.INFO,"Invalid credentials. Please try again.")
            return HttpResponseRedirect(reverse('index'))
    else:
        return HttpResponseRedirect(reverse('index'))

def profile(request):
    return
##find distinct stuff Movie.objects.mongo_find({}).distinct("genres")
def index(request):
    return render(request, 'index.html', {})

@login_required
def movie(request):
    if request.method == "GET":
        mid = request.GET.get("id")
        movie = Movie.objects.filter(imdb_id=mid).first().__dict__
        return render(request,'movie.html',movie)



@login_required
def get_movies(request):
    http = urllib3.PoolManager()
    long = request.GET.get("longitude")
    lat = request.GET.get("latitude")
    if long is None or lat is None:
        return HttpResponseBadRequest
    result = json.loads(http.request("GET","api.openweathermap.org/data/2.5/weather?lat="+str(lat)+"&lon="+str(long)+"&APPID=940f1d33cdc8aa5815a5307279123be4").data)
    #result["weather"][0]["id"]=2222
    weather_id = result["weather"][0]["id"]
    if (weather_id >= 200 and weather_id <=232) or (weather_id>=701 and weather_id<=781): #thunderstorm, disasters
        mov = Movie.objects.filter(genres=["Thriller"])
        cnt = mov.count()
        slice = random.random()*(cnt-10)
        thrillers = list(mov[slice:slice+10])
        hor = Movie.objects.filter(genres = ["Horror"])
        cnt = hor.count()
        slice = random.random()*(cnt-10)
        horrors = random.sample(list(hor[slice:slice+10]),10)
        movies = []
        movies.extend(thrillers)
        movies.extend(horrors)
    elif (weather_id >=500 and weather_id <=531) or (weather_id>=300 and weather_id<=321): #rain
        mov = Movie.objects.filter(genres=["Drama"])
        cnt = mov.count()
        slice = random.random()*(cnt-10)
        movies = []
        movies.extend(mov[slice:slice+10])
        mov = Movie.objects.filter(genres=["Mystery"])
        cnt = mov.count()
        slice = random.random()*(cnt-10)
        movies.extend(list(mov[slice:slice+10]))
    elif(weather_id>=600 and weather_id<=622):
        mov = Movie.objects.filter(genres=["Romance"])
        cnt = mov.count()
        slice = random.random()*(cnt-10)
        movies = []
        movies.extend(mov[slice:slice+10])
        mov = Movie.objects.filter(genres=["Family"])
        cnt = mov.count()
        slice = random.random()*(cnt-10)
        movies.extend(list(mov[slice:slice+10]))
    else:
        mov = Movie.objects.filter(genres=["Action"])
        cnt = mov.count()
        slice = random.random()*(cnt-10)
        movies = []
        movies.extend(mov[slice:slice+10])
        mov = Movie.objects.filter(genres=["Comedy"])
        cnt = mov.count()
        slice = random.random()*(cnt-10)
        movies.extend(list(mov[slice:slice+10]))
    return JsonResponse({"weather":json.dumps(result),"movies":serializers.serialize('json',movies)})

