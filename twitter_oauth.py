#!/usr/bin/python
"""Twitter OAuth code.

Mostly copied from https://github.com/wasauce/tweepy-examples .
"""

__author__ = ['Ryan Barrett <portablecontacts@ryanb.org>']

import appengine_config
import tweepy

from google.appengine.ext import webapp
from google.appengine.ext import db

CALLBACK = 'http://%s/oauth/callback' % appengine_config.HOST


class OAuthToken(db.Model):
  """Datastore model class for an OAuth token.
  """
  token_key = db.StringProperty(required=True)
  token_secret = db.StringProperty(required=True)


class MainPage(RequestHandler):
  """The initial page.
  """

  def get(self):
    # Build a new oauth handler and display authorization url to user.
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK)
    try:
      print template.render('oauth_example/main.html', {
          'authurl': auth.get_authorization_url(),
          'request_token': auth.request_token
      })
    except tweepy.TweepError, e:
      # Failed to get a request token
      print template.render('error.html', {'message': e})
      return

    # We must store the request token for later use in the callback page.
    request_token = OAuthToken(
        token_key = auth.request_token.key,
        token_secret = auth.request_token.secret
    )
    request_token.put()


class CallbackPage(RequestHandler):
  """The OAuth callback.
  """

  def get(self):
    oauth_token = self.request.get('oauth_token', None)
    oauth_verifier = self.request.get('oauth_verifier', None)
    if oauth_token is None:
      # Invalid request!
      print template.render('error.html', {
          'message': 'Missing required parameters!'
      })
      return

    # Lookup the request token
    request_token = OAuthToken.gql('WHERE token_key=:key', key=oauth_token).get()
    if request_token is None:
      # We do not seem to have this request token, show an error.
      print template.render('error.html', {'message': 'Invalid token!'})
      return

    # Rebuild the auth handler
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_request_token(request_token.token_key, request_token.token_secret)

    # Fetch the access token
    try:
      auth.get_access_token(oauth_verifier)
    except tweepy.TweepError, e:
      # Failed to get access token
      print template.render('error.html', {'message': e})
      return

    # So now we could use this auth handler.
    # Here we will just display the access token key&secret
    print template.render('oauth_example/callback.html', {
      'access_token': auth.access_token,
    })


class PostTweet(RequestHandler):
  """Uses the retrieved access token.
  """
  def post(self):
    tweettext = str(cgi.escape(self.request.get('tweettext')))
    # Normally the key and secret would not be passed but rather
    # stored in a DB and fetched for a user.
    token_key = str(self.request.get('key'))
    token_secret = str(self.request.get('secret'))

    #Here we authenticate this app's credentials via OAuth
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

    #Here we set the credentials that we just verified and passed in.
    auth.set_access_token(token_key, token_secret)

    #Here we authorize with the Twitter API via OAuth
    twitterapi = tweepy.API(auth)

    #Here we update the user's twitter timeline with the tweeted text.
    twitterapi.update_status(tweettext)

    #Now we fetch the user information and redirect the user to their twitter
    # username page so that they can see their tweet worked.
    user = twitterapi.me()
    self.redirect('http://www.twitter.com/%s' % user.screen_name)


def main():
  application = webapp.WSGIApplication(
      [('/twitter_oauth_callback', CallbackHandler)],
      debug=appengine_config.DEBUG)
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
