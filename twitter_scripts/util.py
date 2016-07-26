import sys
import time
# from twilio.rest import TwilioRestClient

def send_notification(message):
	# config = open('config/twilio_config.txt').read().split()
	
	# SID = config[0]
	# token = config[1]
	# from_num = config[2]
	# to_num = config[3]

	# t_client = TwilioRestClient(SID, token)
	# message = t_client.messages.create(body=message, from_=from_num, to=to_num)
	print message

def count_down(minutes=0, seconds=0):
	for i in xrange(minutes*60 + seconds,0,-1):
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