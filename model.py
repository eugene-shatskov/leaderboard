import os
import cgi
import urllib

from google.appengine.ext import ndb
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import jinja2
import webapp2


class UserGameScore(ndb.Model):
    """ Model class for the score data. """
    game = ndb.StringProperty()
    username = ndb.StringProperty()
    score = ndb.IntegerProperty()



