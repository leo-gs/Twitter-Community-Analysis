import base64
import database
import datetime
import json
import requests
import sys

'''
Usage: python search_by_keyword.py config.txt output_database.db keywords.txt
'''

INPUT_TERMS = open(sys.argv[3]).read().split()
NUM_TWEETS = 100

config = open(sys.argv[1]).read().split()
CONSUMER_KEY = config[0]
CONSUMER_SECRET = config[1]
ACCESS_TOKEN = config[2]
ACCESS_TOKEN_SECRET = config[3]

API_ENDPOINT = 'https://api.twitter.com'

''' Pulling from API '''

def authenticate():
	consumer_token = CONSUMER_KEY + ':' + CONSUMER_SECRET
	consumer_token = base64.b64encode(consumer_token.encode('ascii'))

	authorization_header = 'Basic ' + consumer_token
	contenttype_header = 'application/x-www-form-urlencoded;charset=UTF-8.'
	body = 'grant_type=client_credentials'

	result = requests.post(API_ENDPOINT + '/oauth2/token', headers={'Authorization':authorization_header, 'Content-Type':contenttype_header}, params=body)
	content = json.loads(result.content)
	if content['token_type'] != 'bearer':
		print 'error authenticating'
		quit()

	bearer_token = content['access_token']
	return bearer_token

def make_request(bearer_token):
	payload = {'q':' OR '.join(INPUT_TERMS), 'reply_type':'popular'}
	authorization_header = 'Bearer ' + bearer_token

	result = requests.get(API_ENDPOINT + '/1.1/search/tweets.json', headers={'Authorization':authorization_header}, params=payload)
	content = json.loads(result.content)
	return content

''''''


''' Inserting into Database '''

def parse_tweet_type(tweet):
	if tweet['in_reply_to_user_id']:
		return ('reply',tweet['in_reply_to_status_id'],None)
	elif 'quoted_status' in tweet:
		return ('quote',tweet['quoted_status']['id'],tweet['quoted_status']['text'])
	elif 'retweeted_status' in tweet:
		return ('retweet',tweet['retweeted_status']['id'],tweet['retweeted_status']['text'])
	else:
		return ('original',None,None)

def insert_tweet(tweet,db):
	tweet_id,text,favorite_count,retweet_count = tweet['id'],tweet['text'],tweet['favorite_count'],tweet['retweet_count']
	created_at = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
	ttype,parent_id,parent_text = parse_tweet_type(tweet)

	hashtags = tweet['entities']['hashtags']
	hashtags_str = None
	if hashtags:
		hashtags_str = ', '.join([hashtag['text'] for hashtag in hashtags])

	db.insert_tweet(tweet_id,text,parent_text,hashtags_str,created_at,favorite_count,retweet_count,ttype,parent_id)

def insert_user(user,db):
	user_id,description,followers_count,friends_count,name,screen_name,time_zone,url = user['id'],user['description'],user['followers_count'],user['friends_count'],user['name'],user['screen_name'],user['time_zone'],user['url']
	verified,protected = (1 if user['verified'] else 0),(1 if user['protected'] else 0)
	created_at = datetime.datetime.strptime(user['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
	db.insert_user(user_id,created_at,description,followers_count,friends_count,screen_name,name,time_zone,url,verified,protected)

def insert_tweetuser(tweet_id,user_id,db):
	db.insert_tweetuser(tweet_id,user_id)

def parse_and_insert_content(db,content):
	print str(len(content['statuses'])) + ' tweets'
	count_new = 0
	for tweet in content['statuses']:
		if not db.tweet_exists(tweet['id']):
			count_new += 1
			user = tweet['user']
			if not db.user_exists(user['id']):
				insert_user(user,db)

			insert_tweet(tweet,db)
			insert_tweetuser(tweet['id'],user['id'],db)
	print str(count_new) + ' new tweets'
''''''

def run():
	db = database.Database(sys.argv[2])
	try:
		bearer_token = authenticate()
		content = make_request(bearer_token)
		parse_and_insert_content(db,content)
		db.close()
	except KeyboardInterrupt:
		database.close()
		quit()