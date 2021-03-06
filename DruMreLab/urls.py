"""DruMreLab URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.auth.views import LogoutView,LoginView
from . import views

from django.conf.urls.static import static

urlpatterns = [
    path('',views.index,name="index"),
    path('admin/', admin.site.urls),
    path('userlikedmovies/',views.listuserliked),
    path('recommendmovies/',views.recommendMovies),
    path('movies/<int:id>/', views.movieDetail),
    path('likemovie/',views.likemovie),
    path('popularmovies/',views.popularMovies),
    path('register/',views.signup,name="register"),
    path('get_movies',views.get_movies,name="get_movies"),
    path('login/',views.user_login,name="login"),
    path('', include('social_django.urls', namespace='social')),
    path('logout/', LogoutView.as_view(), {'next_page': settings.LOGOUT_REDIRECT_URL},
         name='logout'),
    path('movie/',views.movie),
]
