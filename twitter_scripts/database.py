import datetime
import sqlite3
import sys

class Database:

	def __init__(self,name):
		self.conn = sqlite3.connect(name)
		self.cursor = self.conn.cursor()

		if not self.check_if_tables_created():
			self.create_tables()

	def check_if_tables_created(self):
		query = 'SELECT COUNT(name) FROM sqlite_master WHERE type=\'table\' AND name=\'Tweet\';'
		values = ()
		return self.execute_and_commit(query,values)[0][0] > 0

	def create_tables(self):
		queries = open('create_tables.sql').read().split(';')
		for query in queries:
			self.execute_and_commit(query + ';', ())

	def close(self):
		if self.conn:
			self.conn.commit()
			self.conn.close()

	def convert_to_timedelta(self,utc_dt):
		return (utc_dt - datetime.datetime.utcfromtimestamp(0)).total_seconds()

	def execute_and_commit(self,query,values):
		self.cursor.execute(query,values)
		self.conn.commit()
		return self.cursor.fetchall()

	'''
	Order based on dependencies:
	1. Insert User
	2. Insert Tweet
	3. Insert TweetUser,TweetEntity

	see https://dev.twitter.com/overview/api/ for datatypes
	'''

	'''
	user_id,followers_count,friends_count: int
	description,name,screen_name,time_zone,url: str
	created_at: datetime (UTC timezone)
	verified,protected: boolean
	'''
	def insert_user(self,user_id,created_at,description,followers_count,friends_count,name,screen_name,time_zone,url,verified,protected):
		added_at_delta = self.convert_to_timedelta(datetime.datetime.utcnow())
		created_at_delta = self.convert_to_timedelta(created_at)
		
		query = 'INSERT INTO User VALUES (?,?,?,?,?,?,?,?,?,?,?,?);'
		values = (user_id,added_at_delta,created_at_delta,description,followers_count,friends_count,name,screen_name,time_zone,url,1 if verified else 0,1 if protected else 0)

		return self.execute_and_commit(query,values)

	'''
	tweet_id,favorite_count,retweet_count,parent_id: int
	text,ttype,source: str
	created_at: datetime (UTC timezone)
	'''
	def insert_tweet(self,tweet_id,text,parent_text,created_at,favorite_count,retweet_count,ttype,parent_id,source):
		added_at_delta = self.convert_to_timedelta(datetime.datetime.utcnow())
		created_at_delta = self.convert_to_timedelta(created_at)
		print 'neat'

		query = 'INSERT INTO Tweet VALUES (?,?,?,?,?,?,?,?,?,?,?);'
		values = (tweet_id,text,parent_text,added_at_delta,None,created_at_delta,favorite_count,retweet_count,ttype,parent_id,source)

		self.execute_and_commit(query,values)

	'''
	tweet_id,user_id: int
	'''
	def insert_tweetuser(self,tweet_id,user_id):
		query = 'INSERT INTO TweetUser VALUES (?,?);'
		values = (tweet_id,user_id)

		self.execute_and_commit(query,values)

	def insert_tweetentity(self,tweet_id,entity_type,entity_value):
		query = 'INSERT INTO TweetEntity VALUES (?,?,?)'
		values = (tweet_id,entity_type,entity_value)

		self.execute_and_commit(query,values)

	def user_exists(self,user_id):
		query = 'SELECT COUNT(1) FROM User WHERE user_id=?;'
		values = (user_id,)

		result = self.execute_and_commit(query,values)[0]
		return result[0] > 0

	def tweet_exists(self,tweet_id):
		query = 'SELECT COUNT(1) FROM Tweet WHERE tweet_id=?;'
		values = (tweet_id,)

		result = self.execute_and_commit(query,values)[0]
		return result[0] > 0

	def update_tweet(self,tweet_id,retweet_count,favorite_count):
		updated_at_delta = self.convert_to_timedelta(datetime.datetime.utcnow())

		query = 'UPDATE Tweet SET updated_at=?,retweet_count=?,favorite_count=? WHERE tweet_id=?'
		values = (updated_at_delta,retweet_count,favorite_count,tweet_id)

		self.execute_and_commit(query,values)

	def select_data(self,query):
		return self.execute_and_commit(query,())

