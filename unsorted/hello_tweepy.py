import tweepy
from tweepy import OAuth2BearerHandler
from tweepy import API
#auth = tweepy.OAuth1UserHandler(
#   consumer_key, consumer_secret, access_token, access_token_secret
#)
auth = OAuth2BearerHandler("AAAAAAAAAAAAAAAAAAAAAEeXgAEAAAAAIvV6oTf2oncC9po74jSSZMce0yQ%3DeuHzqPpwZ4n84FamNqbL5m00r1HEOa47D1fqVNelkuDTGRAwxp")
auth_api = API(auth)

    
api = tweepy.API(auth)

public_tweets = api.home_timeline()
for tweet in public_tweets:
    print(tweet.text)