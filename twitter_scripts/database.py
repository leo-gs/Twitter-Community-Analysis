import datetime
import sqlite3
import sys

class Database:

	PENDING = 'pending'
	COMPLETE = 'complete'
	ABORTED = 'aborted'

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

	def get_utc_now_delta(self):
		return self.convert_to_timedelta(datetime.datetime.utcnow())

	def execute_and_commit(self,query,values=()):
		self.cursor.execute(query,values)
		self.conn.commit()
		return self.cursor.fetchall()

	def begin_transaction(self):
		self.cursor.execute('BEGIN;')

	def execute(self,query,values=()):
		self.cursor.execute(query,values)

	def commit(self):
		self.conn.commit()

	def rollback(self):
		self.cursor.execute('ROLLBACK;')
	
	'''
	***

	ADDING TWEETS AND USERS

	***
	'''

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
		added_at_delta = self.get_utc_now_delta()
		created_at_delta = self.convert_to_timedelta(created_at)
		
		query = 'INSERT OR REPLACE INTO User VALUES (?,?,?,?,?,?,?,?,?,?,?,?);'
		values = (user_id,added_at_delta,created_at_delta,description,followers_count,friends_count,name,screen_name,time_zone,url,1 if verified else 0,1 if protected else 0)

		return self.execute_and_commit(query,values)

	'''
	tweet_id,favorite_count,retweet_count,parent_id: int
	text,ttype,source: str
	created_at: datetime (UTC timezone)
	'''
	def insert_tweet(self,tweet_id,text,parent_text,created_at,favorite_count,retweet_count,ttype,parent_id,source):
		added_at_delta = self.get_utc_now_delta()
		created_at_delta = self.convert_to_timedelta(created_at)

		query = 'INSERT OR IGNORE INTO Tweet VALUES (?,?,?,?,?,?,?,?,?,?,?);'
		values = (tweet_id,text,parent_text,added_at_delta,None,created_at_delta,favorite_count,retweet_count,ttype,parent_id,source)

		self.execute_and_commit(query,values)

	'''
	tweet_id,user_id: int
	'''
	def insert_tweetuser(self,tweet_id,user_id):
		query = 'INSERT OR IGNORE INTO TweetUser VALUES (?,?);'
		values = (tweet_id,user_id)

		self.execute_and_commit(query,values)

	'''
	tweet_id: int
	entity_type,entity_value: str
	'''	
	def insert_tweetentity(self,tweet_id,entity_type,entity_value):
		query = 'INSERT INTO TweetEntity VALUES (?,?,?)'
		values = (tweet_id,entity_type,entity_value)

		self.execute_and_commit(query,values)

	'''
	tweet_id: int
	'''
	def tweet_exists(self,tweet_id):
		query = 'SELECT COUNT(1) FROM Tweet WHERE tweet_id=?;'
		values = (tweet_id,)

		result = self.execute_and_commit(query,values)[0]
		return result[0] > 0

	'''
	tweet_id,retweet_count,favorite_count: int
	'''
	def update_tweet(self,tweet_id,retweet_count,favorite_count):
		updated_at_delta = self.get_utc_now_delta()

		query = 'UPDATE Tweet SET updated_at=?,retweet_count=?,favorite_count=? WHERE tweet_id=?'
		values = (updated_at_delta,retweet_count,favorite_count,tweet_id)

		self.execute_and_commit(query,values)

	def select_data(self,query):
		return self.execute_and_commit(query)


	'''
	***

	UPDATING FOLLOWERS

	***
	'''

	'''
	resume_pass: Boolean, whether to resume the current pass or start a new one
	returns number of current pass
	'''
	def begin_updatefollowers_pass(self,resume_pass):
		started_at_delta = self.get_utc_now_delta()

		NEW_PASS = 'INSERT INTO FollowerPasses VALUES (?,?,?);'
		GET_CURRENT_PASS = 'SELECT MAX(pass) FROM FollowerPasses;'
		INSERT_USER_TO_START = 'INSERT INTO UserFollowerProgress VALUES (?,?,?,?,?,?,?,?);'
		SELECT_ALL_USERS = 'SELECT user_id FROM User;'
		SELECT_PENDING_USERS = 'SELECT user_id FROM UserFollowerProgress WHERE status=?'

		if resume_pass and self.follower_pass_in_progress():
			self.current_pass = self.execute_and_commit(GET_CURRENT_PASS)[0][0]
			pending_users = self.execute_and_commit(SELECT_PENDING_USERS,(self.PENDING,))
			return pending_users
		else:
			uids_to_update = self.execute_and_commit(SELECT_ALL_USERS)

			values = (None,started_at_delta,-1)
			self.execute_and_commit(NEW_PASS,values)
			self.current_pass = self.execute_and_commit(GET_CURRENT_PASS)[0][0]
			self.begin_transaction()

			for uid in uids_to_update:
				insert_userid_values = (int(uid[0]),self.PENDING,self.current_pass,None,None,None,None,None)
				self.execute(INSERT_USER_TO_START,insert_userid_values)
			self.commit()
			return uids_to_update


	def finish_updatefollowers_pass(self,abort_pending):
		finished_at_delta = self.get_utc_now_delta()

		UPDATE_PASS = 'UPDATE FollowerPasses SET finished_at=? WHERE pass<=?;'
		UPDATE_USERPROGRESS = 'UPDATE UserFollowerProgress SET status=? WHERE status=?'
		USERS_PENDING = 'SELECT COUNT(1) FROM UserFollowerProgress WHERE status=?'

		userspending_values = (self.PENDING,)
		users_pending = self.execute_and_commit(USERS_PENDING,userspending_values)[0][0] > 0

		try:
			self.begin_transaction()

			if abort_pending:
				userprogress_values = (self.ABORTED,self.PENDING)
				self.execute(UPDATE_USERPROGRESS,userprogress_values)

			if abort_pending or not users_pending:
				pass_values = (finished_at_delta,self.current_pass)
				self.execute(UPDATE_PASS,pass_values)
			
			self.commit()

			self.current_pass = None
		except Exception as ex:
			self.rollback()
			raise ex


	def update_userfollower_relations(self,user_id,follower_ids,started_at_delta,unavailable,capped_at=None):
		REMOVE_OLD_FOLLOWER_RELATIONS = 'DELETE FROM UserFollower WHERE user_id=?;'
		INSERT_USERFOLLOWER = 'INSERT INTO UserFollower VALUES (?,?);'
		FINISH_PASS_ON_USER = 'UPDATE UserFollowerProgress SET status=?,unavailable=?,started_at=?,finished_at=?,capped_at=?,followers_added=? WHERE user_id=? AND pass=?;'

		finished_at_delta = self.get_utc_now_delta()

		try:
			self.begin_transaction()

			if unavailable:
				values = (self.COMPLETE,1,started_at_delta,finished_at_delta,capped_at,0,user_id,self.current_pass)
				self.execute(FINISH_PASS_ON_USER,values)
				self.commit()
			else:
				self.execute(REMOVE_OLD_FOLLOWER_RELATIONS,(user_id,))
				for follower_id in follower_ids:
					values = (user_id,follower_id)
					self.execute(INSERT_USERFOLLOWER,values)
				values = (self.COMPLETE,0,started_at_delta,finished_at_delta,capped_at,len(follower_ids),user_id,self.current_pass)
				self.execute(FINISH_PASS_ON_USER,values)
				self.commit()
		except Exception as ex:
			self.rollback()
			raise ex


	def follower_pass_in_progress(self):
		query = 'SELECT COUNT(1) FROM FollowerPasses WHERE finished_at=?'
		values = (-1,)

		result = self.execute_and_commit(query,values)
		return result[0][0] > 0

	'''
	***

	UPDATING FRIENDS

	***
	'''
	
	def begin_updatefriends_pass(self,resume_pass):
		started_at_delta = self.get_utc_now_delta()

		NEW_PASS = 'INSERT INTO FriendPasses VALUES (?,?,?);'
		GET_CURRENT_PASS = 'SELECT MAX(pass) FROM FriendPasses;'
		INSERT_USER_TO_START = 'INSERT INTO UserFriendProgress VALUES (?,?,?,?,?,?,?,?);'
		SELECT_ALL_USERS = 'SELECT user_id FROM User;'
		SELECT_PENDING_USERS = 'SELECT user_id FROM UserFriendProgress WHERE status=?'

		if resume_pass and self.friend_pass_in_progress():
			self.current_pass = self.execute_and_commit(GET_CURRENT_PASS)[0][0]
			pending_users = self.execute_and_commit(SELECT_PENDING_USERS,(self.PENDING,))
			return pending_users
		else:
			uids_to_update = self.execute_and_commit(SELECT_ALL_USERS)

			values = (None,started_at_delta,-1)
			self.execute_and_commit(NEW_PASS,values)
			self.current_pass = self.execute_and_commit(GET_CURRENT_PASS)[0][0]
			self.begin_transaction()

			for uid in uids_to_update:
				insert_userid_values = (int(uid[0]),self.PENDING,self.current_pass,None,None,None,None,None)
				self.execute(INSERT_USER_TO_START,insert_userid_values)
			self.commit()
			return uids_to_update


	def finish_updatefriends_pass(self,abort_pending):
		finished_at_delta = self.get_utc_now_delta()

		UPDATE_PASS = 'UPDATE FriendPasses SET finished_at=? WHERE pass<=?;'
		UPDATE_USERPROGRESS = 'UPDATE UserFriendProgress SET status=? WHERE status=?'
		USERS_PENDING = 'SELECT COUNT(1) FROM UserFriendProgress WHERE status=?'

		userspending_values = (self.PENDING,)
		users_pending = self.execute_and_commit(USERS_PENDING,userspending_values)[0][0] > 0

		try:
			self.begin_transaction()

			if abort_pending:
				userprogress_values = (self.ABORTED,self.PENDING)
				self.execute(UPDATE_USERPROGRESS,userprogress_values)

			if abort_pending or not users_pending:
				pass_values = (finished_at_delta,self.current_pass)
				self.execute(UPDATE_PASS,pass_values)
			
			self.commit()

			self.current_pass = None
		except Exception as ex:
			self.rollback()
			raise ex


	def update_userfriend_relations(self,user_id,friend_ids,started_at_delta,unavailable,capped_at=None):
		REMOVE_OLD_FRIEND_RELATIONS = 'DELETE FROM UserFriend WHERE user_id=?;'
		INSERT_USERFRIEND = 'INSERT INTO UserFriend VALUES (?,?);'
		FINISH_PASS_ON_USER = 'UPDATE UserFriendProgress SET status=?,unavailable=?,started_at=?,finished_at=?,capped_at=?,friends_added=? WHERE user_id=? AND pass=?;'

		finished_at_delta = self.get_utc_now_delta()

		try:
			self.begin_transaction()

			if unavailable:
				values = (self.COMPLETE,1,started_at_delta,finished_at_delta,capped_at,0,user_id,self.current_pass)
				self.execute(FINISH_PASS_ON_USER,values)
				self.commit()
			else:
				self.execute(REMOVE_OLD_FRIEND_RELATIONS,(user_id,))
				for friend_id in friend_ids:
					values = (user_id,friend_id)
					self.execute(INSERT_USERFRIEND,values)
				values = (self.COMPLETE,0,started_at_delta,finished_at_delta,capped_at,len(friend_ids),user_id,self.current_pass)
				self.execute(FINISH_PASS_ON_USER,values)
				self.commit()
		except Exception as ex:
			self.rollback()
			raise ex


	def friend_pass_in_progress(self):
		query = 'SELECT COUNT(1) FROM FriendPasses WHERE finished_at=?'
		values = (-1,)

		result = self.execute_and_commit(query,values)
		return result[0][0] > 0

	'''
	***
	Calculating shared friends and followers
	***
	'''

	def calculate_sharedfollowers(self):
		query = open('sharedfriends.sql').read()
		self.execute_and_commit(query,())

	def calculate_sharedfriends(self):
		query = open('sharedfriends.sql').read()
		self.execute_and_commit(query,())

