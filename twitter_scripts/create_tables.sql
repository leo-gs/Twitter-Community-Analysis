DROP TABLE IF EXISTS TweetType;
CREATE TABLE TweetType (
	type TEXT PRIMARY KEY
	);
INSERT INTO TweetType VALUES ('retweet'), ('quote'), ('reply'), ('original'), ('other');

DROP TABLE IF EXISTS EntityType;
CREATE TABLE EntityType (
	type TEXT PRIMARY KEY
);
INSERT INTO EntityType VALUES ('hashtag'), ('url'), ('user_mentions'), ('symbols'), ('media'), ('extended');

DROP TABLE IF EXISTS User;
CREATE TABLE User (
	user_id INTEGER PRIMARY KEY, 
	added_at INTEGER,
	created_at INTEGER,
	description TEXT, 
	followers_count INTEGER, 
	friends_count INTEGER, 
	name TEXT, 
	screen_name TEXT, 
	time_zone TEXT, 
	url TEXT, 
	verified INTEGER, 
	protected INTEGER
	);

DROP TABLE IF EXISTS Tweet;
CREATE TABLE Tweet (
	tweet_id INTEGER PRIMARY KEY, 
	text TEXT,
	parent_text TEXT,
	added_at INTEGER, 
	created_at INTEGER, 
	fav_count INTEGER, 
	retweet_count INTEGER, 
	type TEXT, 
	parent_id INTEGER,
	source TEXT,
	FOREIGN KEY(type) REFERENCES TweetType(type)
	);

DROP TABLE IF EXISTS TweetUser;
CREATE TABLE TweetUser (
	tweet_id INTEGER PRIMARY KEY,
	user_id INTEGER,
	FOREIGN KEY(tweet_id) REFERENCES Tweet(tweet_id),
	FOREIGN KEY(user_id) REFERENCES User(user_id)
);

DROP TABLE IF EXISTS TweetEntity;
CREATE TABLE TweetEntity (
	tweet_id INTEGER,
	entity_type TEXT,
	entity_value TEXT,
	FOREIGN KEY(entity_type) REFERENCES EntityType(type)
);