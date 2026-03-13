import tweepy
from tweepy import OAuth2BearerHandler
from tweepy import API
from keys import TWITTER_BEARER_TOKEN
#auth = tweepy.OAuth1UserHandler(
#   consumer_key, consumer_secret, access_token, access_token_secret
#)
auth = OAuth2BearerHandler(TWITTER_BEARER_TOKEN)
auth_api = API(auth)

    
api = tweepy.API(auth)

public_tweets = api.home_timeline()
for tweet in public_tweets:
    print(tweet.text)