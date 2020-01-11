import json
import os
import django
import re
import urllib3
import base64
os.environ["DJANGO_SETTINGS_MODULE"] = 'DruMreLab.settings'
django.setup()

from DruMreLab.models import *

from pymongo import MongoClient
client = MongoClient()
client = MongoClient('localhost', 27017)

#for res in client.drummre.DruMreLab_movie.find({ "genres": { "$all": ["Comedy", "Romance"] } }):
for res in Movie.objects.filter(original_title__icontains="pulp fiction"):#mongo_find({"original_title":re.compile("pulp fiction",re.IGNORECASE)}):
    print(res)