from djongo import models

class Movie(models.Model):
    adult = models.BooleanField()
    backdrop_path = models.CharField(max_length=100)
    belongs_to_collection = models.CharField(max_length=100)
    budget = models.IntegerField()
    genres = models.ListField()
    homepage = models.CharField(max_length= 100)
    id = models.IntegerField(primary_key = True)
    imdb_id =  models.CharField(max_length= 100)
    original_language =  models.CharField(max_length= 100)
    original_title =  models.CharField(max_length= 200)
    overview =  models.CharField(max_length= 1000)
    popularity = models.FloatField()
    poster_path =  models.CharField(max_length= 100)
    production_companies = models.ListField()
    production_countries = models.ListField()
    release_date =  models.CharField(max_length= 100)
    revenue = models.IntegerField()
    runtime = models.IntegerField()
    spoken_languages = models.ListField()
    status =  models.CharField(max_length= 100)
    tagline =  models.CharField(max_length= 100)
    title =  models.CharField(max_length= 100)
    video = models.BooleanField()
    vote_average = models.FloatField()
    vote_count = models.IntegerField()

    objects = models.DjongoManager()

class UserLikedMovies(models.Model):
    user_id = models.CharField(max_length = 100)
    liked_movies = models.ListField()

class Review(models.Model):
    imdb_id = models.CharField(max_length = 100)
    total_results = models.IntegerField()
    total_pages = models.IntegerField()
    id = models.IntegerField(primary_key = True)
    results = models.ListField()

class Credits(models.Model):
    id = models.IntegerField(primary_key = True)
    cast = models.ListField()
    crew = models.ListField()
    imdb_id =  models.CharField(max_length= 100)

