import database
import sys
import time
import tweepy

CAP = 500
ABORT_WHEN_INTERRUPTED = False

def authenticate():
	config = open(sys.argv[1]).read().split()

	consumer_key = config[0]
	consumer_secret = config[1]
	access_token = config[2]
	access_token_secret = config[3]

	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)

	api = tweepy.API(auth)
	return api

def get_follower_ids_from_id(uid,api):
	ids = []
	try:
		for page in tweepy.Cursor(api.followers_ids, id=uid).pages():
			ids.extend(page)
			time.sleep(1*60)
			if CAP and len(ids) > CAP:
				return ids[:CAP]
	except tweepy.RateLimitError:
		time.sleep(15*60)
		ids = get_follower_ids_from_id(uid)
	return ids

def run():
	api = authenticate()
	db = database.Database(sys.argv[2])
	should_resume = db.follower_pass_in_progress()
	users = db.begin_updatefollowers_pass(should_resume)

	for user in users:
		uid = user[0]
		started_at_delta = db.get_utc_now_delta()
		try:
			follower_ids = get_follower_ids_from_id(uid,api)
			db.update_userfollower_relations(uid,follower_ids,started_at_delta,False,capped_at=CAP)
		except tweepy.error.TweepError as ex:
			print ex
			db.update_userfollower_relations(uid,[],started_at_delta,True,capped_at=CAP)
			time.sleep(1*60)
		except KeyboardInterrupt:
			db.finish_updatefollowers_pass(ABORT_WHEN_INTERRUPTED)
			quit()

	db.finish_updatefollowers_pass(ABORT_WHEN_INTERRUPTED)

run()