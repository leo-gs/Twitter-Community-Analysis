import base64
import database
import datetime
import json
import requests
import sqlite3
import sys
import tweepy

'''
Usage: python collect_by_term.py config.txt output_database.db keywords.txt
'''

INPUT_TERMS = open(sys.argv[3]).read().split()
NUM_TWEETS = 100

config = open(sys.argv[1]).read().split()
CONSUMER_KEY = config[0]
CONSUMER_SECRET = config[1]
ACCESS_TOKEN = config[2]
ACCESS_TOKEN_SECRET = config[3]

''' Pulling from API '''

def authenticate():
	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

	api = tweepy.API(auth)
	return api

''''''


''' Inserting into Database '''

def parse_tweet_type(tweet):
	if tweet.in_reply_to_user_id:
		return ('reply',tweet.in_reply_to_status_id,None)
	elif tweet.is_quote_status and hasattr(tweet,'quoted_status'):
		return ('quote',tweet.quoted_status.id,tweet.quoted_status.text)
	elif hasattr(tweet,'retweeted_status'):
		return ('retweet',tweet.retweeted_status.id,tweet.retweeted_status.text)
	else:
		return ('original',None,None)

def insert_tweet(tweet,db):
	tweet_id,text,favorite_count,retweet_count,source = tweet.id,tweet.text,tweet.favorite_count,tweet.retweet_count,tweet.source
	created_at = tweet.created_at
	ttype,parent_id,parent_text = parse_tweet_type(tweet)

	db.insert_tweet(tweet_id,text,parent_text,created_at,favorite_count,retweet_count,ttype,parent_id,source)

def insert_tweetentities(tweet,db):
	hashtags = tweet.entities['hashtags']
	for hashtag in hashtags:
		db.insert_tweetentity(tweet.id,'hashtag',hashtag['text'])

	urls = tweet.entities['urls']
	for url in urls:
		db.insert_tweetentity(tweet.id,'url',url['expanded_url'])

	symbols = tweet.entities['symbols']
	for symbol in symbols:
		db.insert_tweetentity(tweet.id,'symbol',symbol['text'])

	umentions = tweet.entities['user_mentions']
	for umention in umentions:
		db.insert_tweetentity(tweet.id,'user_mention',umention['screen_name'])

	if 'media' in tweet.entities:
		media = tweet.entities['media']
		for medium in media:
			db.insert_tweetentity(tweet.id,'media',medium['expanded_url'])

	if 'extended_entities' in tweet.entities:
		extendeds = tweet.entities['extended_entities']
		for extended in extendeds:
			db.insert_tweetentity(tweet.id,'extended',extended['expanded_url'])

def insert_user(user,db):
	user_id,description,followers_count,friends_count,name,screen_name,time_zone,url = user.id,user.description,user.followers_count,user.friends_count,user.name,user.screen_name,user.time_zone,user.url
	verified,protected = (1 if user.verified else 0),(1 if user.protected else 0)
	created_at = user.created_at
	db.insert_user(user_id,created_at,description,followers_count,friends_count,screen_name,name,time_zone,url,verified,protected)


''''''

class StreamListener(tweepy.StreamListener):

	def on_status(self,tweet):
		try:
			user = tweet.user
			if not self.db.user_exists(user.id):
				insert_user(user,self.db)

			insert_tweet(tweet,self.db)
			insert_tweetentities(tweet,self.db)
			self.db.insert_tweetuser(tweet.id,user.id)
		except sqlite3.InterfaceError:
			pass

def run():
	listener = StreamListener()
	listener.db = database.Database(sys.argv[2])
	api = authenticate()
	try:
		stream = tweepy.Stream(auth=api.auth, listener=listener)
		stream.filter(track=INPUT_TERMS,languages=['en'])
	except KeyboardInterrupt:
		listener.db.close()
		quit()

run()
