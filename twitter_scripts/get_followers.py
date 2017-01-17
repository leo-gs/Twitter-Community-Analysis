import csv
import datetime
import json
import sys
import time
from time import strftime
import tweepy
from util import send_notification

config = open(sys.argv[1]).read().split()
consumer_key = config[0]
consumer_secret = config[1]
access_token = config[2]
access_token_secret = config[3]

wait_time = 15

INPUT_FILENAME = 'data/screenname_to_user_data.json'
OUTPUT_FILENAME = 'data/screenname_to_follower_id.json'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

users_to_followers = json.load(open(OUTPUT_FILENAME))

user_data = json.load(open(INPUT_FILENAME))
# users = user_data.keys()

already_collected = set()

capped_followers = json.load(open('data/capped_followers.json'))

def get_already_collected():
	reader = csv.reader(open('data/user_to_follower_edges.csv'))
	reader.next()
	for row in reader:
		already_collected.add(row[1])

def get_follower_ids_from_screenname(screenname):
	ids = []
	for page in tweepy.Cursor(api.followers_ids, screen_name=screenname).pages():
		ids.extend(page)
		count_down(1)
		if len(ids) > 20000:
			capped_followers[screenname] = user_data[screenname]['followers_count']
			break
	update_str = str(len(users_to_followers.keys()) + len(protected_users)) + '/' + str(len(users)) + ' collected: ' + screenname + ' ' + str(len(ids))
	remaining_secs = (len(users) - len(protected_users) - len(users_to_followers.keys())) * 70
	comp_time = datetime.datetime.fromtimestamp(int(datetime.datetime.now().strftime('%s')) + remaining_secs)
	update_str = update_str + '; estimated completion time: ' + comp_time.strftime('%a %H:%M')
	print (update_str)
	return ids

def should_get_user_info(screenname):
	no_info = (screenname not in users_to_followers.keys()) and (user_data[screenname]['id'] not in already_collected)
	protected = screenname in protected_users
	return no_info and not protected

def print_update():
	sys.stdout.write('\n' + str(len(users_to_followers.keys()) + len(protected_users)) + '/' + str(len(users)) + ' collected')
	sys.stdout.flush()

def dump():
	print_update()
	json.dump(users_to_followers, open(OUTPUT_FILENAME, 'w'))
	json.dump(capped_followers, open('data/capped_followers.json', 'w'))
	# json.dump(protected_users, open('data/protected_users.json', 'w'))

def run():
	try:
		for user in users:
			if user[-1] == '\"':
				user = user[:-1]
			print (user)
			if should_get_user_info(user):
				try:
					users_to_followers[user] = get_follower_ids_from_screenname(user)
				except tweepy.RateLimitError:
					json.dump(users_to_followers, open(OUTPUT_FILENAME, 'w'))
					count_down(15)
				except tweepy.error.TweepError as ex:
					print ex
					protected_users.append(user)
					count_down(1)
		dump()
	except KeyboardInterrupt:
		dump()
		quit()

def count_down(minutes):
	try:
		for i in xrange(minutes * 60,0,-1):
		    time.sleep(1)
		    min_str = str(i/60)
		    sec_str = str(i%60)
		    if (i/60 < 10):
		    	min_str = '0' + min_str
		    if (i%60 < 10):
		    	sec_str = '0' + sec_str
		    time_str = '\tTime until next request: ' + min_str+':'+sec_str + '\r'
		    sys.stdout.write(time_str + ' ')
		    sys.stdout.flush()
	except KeyboardInterrupt:
		print_update()
		json.dump(users_to_followers, open(OUTPUT_FILENAME, 'w'))
		quit()

users = []
for user in user_data:
	if user not in users_to_followers.keys():
		users.append(user)
users.sort(key=lambda uname:user_data[uname]['followers_count'])
protected_users = json.load(open('data/protected_users.json'))
while (len(users) > 0):
	try:
		users = []
		for user in user_data:
			if user not in users_to_followers.keys():
				users.append(user)
			users.sort(key=lambda uname:user_data[uname]['followers_count'])
		print (len(users))
		run()
	except KeyboardInterrupt:
		dump()
		quit()
	# except:
	# 	dump()
	# 	send_notification('Error encountered. Quiting.')
	# 	quit()

send_notification('\nAll followers collected.')