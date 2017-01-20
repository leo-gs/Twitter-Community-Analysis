These scripts use the [Tweepy API](http://docs.tweepy.org/en/v3.5.0/api.html) and the [Twitter REST API](https://dev.twitter.com/rest/public).

Before Doing Anything
=
1.) Setup tweepy by navigating to **tweepy** and running the command `python setup.py`.

2.) Get a Twitter API key [here](https://apps.twitter.com/app/new).  Fill in **twitter_scripts/config/twitter_config.txt** with the access keys/tokens/secrets.  Twitter rate limits each key separately, so you can generate multiple access keys and save them in multiple .txt files if you want do multiple things at once.

Follower and Following Relations
=
- To get follower relations: run the command `python update_followers.py config/twitter_config.txt DATABASE.db`.  This will populate the **UserFollower** table in the database which maps user ids to follower ids, as well as UserFollowerProgress, and FollowerPasses, which store information about when user-follower relations are updated.  `CAP` in `update_followers.py` can be set to the maximum number of followers gathered for each users.  This is helpful for when some users have lots of followers.  `ABORT_WHEN_INTERRUPTED` should be set to `False` if you want to pause your session with a `KeyboardInterrupt`.  If set to `True`, it will start over when interrupted.
- The instructions for the friend relations are the same as those for the follower relations above.
- These can take a really long time because of rate limiting.

Union and Intersection of Friends and Followers
=
Run the command `python make_union_and_intersection_weights.py`.  This will output three .csv files of the form **screen name 1, screen name 2, |intersection|, |union|,|intersection|/|union|**.
- **data/weights_followers.csv**: shared followers
- **data/weights_friends.csv**: shared friends
- **data/weights.csv**: shared friends and followers

Updating Retweet and Favorite Counts
=
Given a SQLite3 database populated with Tweets as created by the Streaming or Searching scripts described below, this script updates the retweet and favorite count for each tweet.  If the tweet data cannot be found, the values will not be changed.  To run the script, run the command `python update_tweets.py config/tweetids.txt DATABASE.db`, where **DATABASE.db** is the SQLite3 database.

Streaming and Searching by Keyword
=
`stream_by_keywords.py` and `search_by_keywords.py` each take 3 parameters: a file with Twitter API keys (as described above), the name of the output sqlite3 database, and a .txt file with a list of newline-separated keywords. Right now this script only searches for English-language tweets, but this can be modified. If the given database does not exist or does not have the correct tables, a new one will be created. If it does exist and has the correct tables, it will be added to. In the database, there are four tables holding your data:
- **Tweet**: contains tweet data at the time of being captured
- **User**: contains user data at the time of being captured
- **TweetUser**: links each tweet to the user who tweeted it
- **TweetEntity**: contains the entities (hashtags, user mentions, symbols, urls) of a tweet at the time of being captured
The script used to create these tables is `create_tables.sql`.

For more reference, visit the [Twitter Search API](https://dev.twitter.com/rest/public/search) or the [Twitter Streaming API](https://dev.twitter.com/streaming/public).
