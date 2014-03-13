import os
import cgi
import urllib
import json
import logging

from google.appengine.ext import ndb
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import webapp2

from model import UserGameScore


def convert_to_json(list):
    """ Convert the list to a dict.  Each item in the list is a UserGameScore
    model object. """
    return [u.to_dict() for u in list]


def get_all_games():
    """ Return a list of all games stored """
    results = UserGameScore.query(projection=["game"], distinct=True).order(
        UserGameScore.game).fetch()
    return convert_to_json(results)


def get_all_users():
    """ Return a list of all users stored """
    results = UserGameScore.query(projection=["username"], distinct=True).order(
        UserGameScore.username).fetch()
    return convert_to_json(results)


def get_top_ten_leaderboard(game):
    """ Return a list of the top 10 scores in the leaderboard for the given
    game. """
    results = UserGameScore.query(UserGameScore.game == game).order(
        -UserGameScore.score).fetch(10)
    return convert_to_json(results)


def get_leaderboard(game):
    """ Return a list of the all scores in the leaderboard for the given
    game. """
    results = UserGameScore.query(UserGameScore.game == game).order(
        -UserGameScore.score).fetch()
    return convert_to_json(results)


def get_user_high_score(game, user):
    """ Return the user's high score for the given game. """
    return UserGameScore.query(UserGameScore.game == game,
                               UserGameScore.username == user).get().score


def get_user_all_scores(user):
    """ Return all of the user's high scores, across all games played. """
    results = UserGameScore.query(UserGameScore.username == user).order(
        UserGameScore.game).fetch()
    return convert_to_json(results)


def encode_id(game, user):
    """ Create the id/key name for the UserGameScore entry """
    return game + "_" + user


@ndb.transactional
def save_score(user_string, game_string, score_string):
    """ Store the user, game, and score into the datastore """
    score_int = int(score_string)
    score_entry = UserGameScore.get_by_id(encode_id(game_string, user_string))
    if (score_entry is None):
        # Create a new UserGameScore object
        score_entry = UserGameScore(game = game_string, username = user_string,
                                    score = score_int)
        score_entry.key = ndb.Key("UserGameScore",
                                  encode_id(game_string, user_string))
        score_entry.put()
    else:
        if (score_int > score_entry.score):
            score_entry.score = score_int
            score_entry.put()


class SaveScoreHandler(webapp2.RequestHandler):
    """ Handler class for storing a user's score """

    @staticmethod
    def check_input_null(arg_string):
        """ Checks if the given argument string is undefined or has 0 length """
        return (arg_string is None or len(arg_string) == 0)

    @staticmethod
    def validate(self, req):
        """ Validate the request parameters """
        if (self.check_input_null(req["game"]) or
            self.check_input_null(req["username"]) or
            self.check_input_null(req["score"])):
            return False
        if (req["score"].isdigit() == False):
            return False
        return True

    def post(self):
        """ Store the score """
        logging.info(self.request)
        req = json.loads(self.request.body)
        if (self.validate(self, req)):
            save_score(req["username"], req["game"], req["score"])
            self.response.write("")
        else:
            self.error(400)
            self.response.write("The score data is invalid.")


class GetLeaderboardHandler(webapp2.RequestHandler):
    """ Handler class for returning a leaderboard """

    def get(self, game):
        leaderboard = get_top_ten_leaderboard(game)
        if (leaderboard is None or len(leaderboard) == 0):
            self.error(404)
            self.response.write("There is no leaderboard associated with '" +
                                game + "'.")
        self.response.write(json.dumps(leaderboard))


class GetUserHandler(webapp2.RequestHandler):
    """ Handler class for returning the user's scores """

    def get(self, user):
        gamelist = get_user_all_scores(user)
        if (gamelist is None or len(gamelist) == 0):
            self.error(404)
            self.response.write("There are no scores associated with '" +
                                user + "'.")
        self.response.write(json.dumps(gamelist))


application = webapp2.WSGIApplication([
        ('/api/save', SaveScoreHandler),
        ('/api/games/(\w+)', GetLeaderboardHandler),
        ('/api/users/(\w+)', GetUserHandler)
        ], debug=True)

if __name__ == "__main__":
    run_wsgi_app(application)

