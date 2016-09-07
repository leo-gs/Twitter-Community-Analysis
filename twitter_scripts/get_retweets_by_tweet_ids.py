import base64
import csv
import json
import sys
import urllib
import urllib2

''' Usage: python get_retweets_by_tweet_ids.py data/csv_file_of_ids.csv config/file_with_consumer_key_and_secret.txt '''

def get_consumer_key_and_secret():
	config = open(sys.argv[2]).read().split()
	consumer_key_and_secret = [config[0], config[1]]
	return consumer_key_and_secret

def get_oauth_token(consumer_key, consumer_secret):
	''' Reference: https://dev.twitter.com/oauth/application-only '''
	b64_encoded = base64.b64encode(consumer_key + ":" + consumer_secret)
	oauth_endpoint = "https://api.twitter.com/oauth2/token"
	oauth_request_headers = {"Authorization" : "Basic " + b64_encoded, "Content-Type" : "application/x-www-form-urlencoded;charset=UTF-8"}
	oauth_request_body = "grant_type=client_credentials"

	auth_request = urllib2.Request(oauth_endpoint, headers=oauth_request_headers, data=oauth_request_body)
	auth_response = json.load(urllib2.urlopen(auth_request))

	return auth_response["access_token"]

def make_request(access_token, ids):
	''' ids is a comma-separated list of tweet ids. Reference: https://dev.twitter.com/rest/reference/get/statuses/lookup '''
	twitter_endpoint = "https://api.twitter.com/1.1/statuses/lookup.json"
	twitter_request_headers = {"Authorization": "Bearer " + access_token}
	twitter_request_parameters = {"id" : ",".join(ids), "map" : "true"}

	twitter_request = urllib2.Request(twitter_endpoint + "?" + urllib.urlencode(twitter_request_parameters), headers = twitter_request_headers)
	twitter_response = json.load(urllib2.urlopen(twitter_request))

	return twitter_response

def load_tweet_ids_from_csv():
	csvreader = csv.reader(open(sys.argv[1]))
	csvreader.next() # remove header
	tweet_ids = []
	for row in csvreader:
		if (row[0] != ""):
			tweet_ids.append(row[0])
	print str(len(tweet_ids)) + " tweets ids loaded"
	return tweet_ids

def write_to_csv(data):
	header = ["tweet_id", "rt_count"]
	writer = csv.writer(open(sys.argv[1].split('.')[0] + "_retweets.csv", "w+"))
	writer.writerow(header)
	for tweet_id, rt_count in data.items():
		writer.writerow([tweet_id, rt_count])

consumer_key_and_secret = get_consumer_key_and_secret()
token = get_oauth_token(consumer_key=consumer_key_and_secret[0], consumer_secret=consumer_key_and_secret[1])

tweet_ids = load_tweet_ids_from_csv()
id_to_rt_count = {}

start_index = 0
end_index = 100
while start_index < len(tweet_ids):
	if end_index > len(tweet_ids):
		end_index = len(tweet_ids)
	response = make_request(token, tweet_ids[start_index:end_index])
	for tweet_id, tweet_data in response["id"].items():
		print tweet_data
		rt_count = None
		if tweet_data != None:
			rt_count = tweet_data["retweet_count"]
		id_to_rt_count[tweet_id] = rt_count
	start_index = end_index
	end_index += 100

write_to_csv(id_to_rt_count)

print "Done!"
