import base64
import database
import csv
import json
import sys
import time
import urllib
import urllib2

''' Usage: python get_retweets_by_tweet_ids.py config/file_with_consumer_key_and_secret.txt INPUT_SQLITE.db '''

SQL_QUERY = 'SELECT tweet_id FROM Tweet;' # edit this to make it more specific, but make sure it only returns tweet ids

def get_consumer_key_and_secret():
	config = open(sys.argv[1]).read().split()
	consumer_key_and_secret = [config[0], config[1]]
	return consumer_key_and_secret

def get_oauth_token(consumer_key, consumer_secret):
	''' Reference: https://dev.twitter.com/oauth/application-only '''
	b64_encoded = base64.b64encode(consumer_key + ':' + consumer_secret)
	oauth_endpoint = 'https://api.twitter.com/oauth2/token'
	oauth_request_headers = {'Authorization' : 'Basic ' + b64_encoded, 'Content-Type' : 'application/x-www-form-urlencoded;charset=UTF-8'}
	oauth_request_body = 'grant_type=client_credentials'

	auth_request = urllib2.Request(oauth_endpoint, headers=oauth_request_headers, data=oauth_request_body)
	auth_response = json.load(urllib2.urlopen(auth_request))

	return auth_response['access_token']

def make_request(access_token, ids):
	''' ids is a comma-separated list of tweet ids. Reference: https://dev.twitter.com/rest/reference/get/statuses/lookup '''
	twitter_endpoint = 'https://api.twitter.com/1.1/statuses/lookup.json'
	twitter_request_headers = {'Authorization':'Bearer '+access_token}
	twitter_request_parameters = {'id':','.join(ids), 'map':'true'}

	twitter_request = urllib2.Request(twitter_endpoint + '?' + urllib.urlencode(twitter_request_parameters), headers = twitter_request_headers)
	twitter_response = None
	try:
		twitter_response = json.load(urllib2.urlopen(twitter_request))
	except urllib2.HTTPError:
		time.sleep(15*60)
		twitter_response = json.load(urllib2.urlopen(twitter_request))

	return twitter_response

consumer_key_and_secret = get_consumer_key_and_secret()
token = get_oauth_token(consumer_key=consumer_key_and_secret[0], consumer_secret=consumer_key_and_secret[1])

start_index = 0
end_index = 100

db = database.Database(sys.argv[2])
tweet_ids = [str(elt[0]) for elt in db.select_data(SQL_QUERY)]

progress = 0
while start_index < len(tweet_ids):
	if end_index > len(tweet_ids):
		end_index = len(tweet_ids)
	response = make_request(token, tweet_ids[start_index:end_index])
	for tweet_id, tweet_data in response['id'].items():
		retweet_count,favorite_count = None,None
		if tweet_data != None:
			retweet_count = tweet_data['retweet_count']
			favorite_count = tweet_data['favorite_count']
			db.update_tweet(tweet_id,retweet_count,favorite_count)
		progress += 1
		sys.stdout.write('\r' + ('%.2f' % ((100.0*progress)/len(tweet_ids))) + '%\t')
	start_index = end_index
	end_index += 100

print ('Done!')
