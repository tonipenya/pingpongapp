from google.appengine.ext import db
from django.contrib.auth.models import User

class Club(db.Model):
  owner = db.ReferenceProperty(User)
  name = db.StringProperty(required=True)
  date_created = db.DateTimeProperty(auto_now_add=True)
