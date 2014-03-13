import os
import cgi
import urllib

from google.appengine.ext import ndb
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import jinja2
import webapp2
import model
import api

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainPage(webapp2.RequestHandler):
    """ Main home page """
    def get(self):
        template_values = {}
        template = JINJA_ENVIRONMENT.get_template('templates/main.template')
        self.response.write(template.render(template_values))


class SaveScorePage(webapp2.RequestHandler):
    """ Page for storing a score """
    def get(self):
        """ Display a form for saving a username, game, and score. """
        template_values = {}
        template = JINJA_ENVIRONMENT.get_template('templates/save.template')
        self.response.write(template.render(template_values))


class GamesPage(webapp2.RequestHandler):
    """ Lists all of the games currently in the datastore """
    def get(self):
        gamelist = api.get_all_games()
        template_values = {
            'gamelist': gamelist
        }
        template = JINJA_ENVIRONMENT.get_template('templates/game.template')
        self.response.write(template.render(template_values))


class GameLeaderboardPage(webapp2.RequestHandler):

    def get(self, game):
        """ Display the leaderboard for the given game """
        leaderboard = api.get_top_ten_leaderboard(game)
        template_values = {
            'game': game,
            'leaderboard': leaderboard,
        }
        template = JINJA_ENVIRONMENT.get_template(
            'templates/leaderboard.template')
        self.response.write(template.render(template_values))


class UsersPage(webapp2.RequestHandler):

    def get(self):
        """ Retrieve and list all of the users currently in the datastore """
        userlist = api.get_all_users()
        template_values = {
            'userlist': userlist
        }
        template = JINJA_ENVIRONMENT.get_template('templates/user.template')
        self.response.write(template.render(template_values))


class UserScorePage(webapp2.RequestHandler):

    def get(self, user):
        """ Display all of the high scores for the given user """
        gamelist = api.get_user_all_scores(user)
        template_values = {
            'user': user,
            'gamelist': gamelist,
        }
        template = JINJA_ENVIRONMENT.get_template(
            'templates/userboard.template')
        self.response.write(template.render(template_values))


application = webapp2.WSGIApplication([
        ('/main', MainPage),
        ('/save', SaveScorePage),
        ('/games', GamesPage),
        ('/games/(\w+)', GameLeaderboardPage),
        ('/users', UsersPage),
        ('/users/(\w+)', UserScorePage)
        ], debug=True)

if __name__ == "__main__":
    run_wsgi_app(application)

