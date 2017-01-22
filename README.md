The purpose of this library is to enable community analysis based on tweets captured by either the streaming or search API. Data is stored in sqlite databases. These scripts use the [Tweepy API](http://docs.tweepy.org/en/v3.5.0/api.html) and the [Twitter REST API](https://dev.twitter.com/rest/public).

Before Doing Anything
=
1.) Make sure you have all the necessary libraries installed, including Tweepy.

2.) Get a Twitter API key [here](https://apps.twitter.com/app/new).  Fill in **twitter_scripts/config/twitter_config.txt** with the access keys/tokens/secrets.

Streaming and Searching by Keyword
=
`stream_by_keywords.py` and `search_by_keywords.py` each take 3 parameters: a file with Twitter API keys (as described above), the name of the output sqlite3 database, and a .txt file with a list of newline-separated keywords. Right now this script only searches for English-language tweets, but this can be modified. If the given database does not exist or does not have the correct tables, a new one will be created. If it does exist and has the correct tables, it will be added to. In the database, there are four tables holding your data:
- **Tweet**: contains tweet data at the time of being captured
- **User**: contains user data at the time of being captured
- **TweetUser**: links each tweet to the user who tweeted it
- **TweetEntity**: contains the entities (hashtags, user mentions, symbols, urls) of a tweet at the time of being captured
The script used to create these tables is `create_tables.sql`.

Follower and Following Relations
=
- To get follower relations: run the command `python update_followers.py config/twitter_config.txt DATABASE.db`.  This will populate the **UserFollower** table in the database which maps user ids to follower ids, as well as **UserFollowerProgress**, and **FollowerPasses**, which store information about when user-follower relations are updated.  `CAP` in `update_followers.py` can be set to the maximum number of followers gathered for each users.  This is helpful for when some users have lots of followers.  `ABORT_WHEN_INTERRUPTED` should be set to `False` if you want to pause your session with a `KeyboardInterrupt`.  If set to `True`, it will start over when interrupted.
- The instructions for the friend relations are the same as those for the follower relations above.
- These can take a really long time because of rate limiting.

Calculating similarity (Jaccard index) of  users' friends and followers.
=
Run the command `python calculate_sharedfollowers.py DATABASE.db`.  As long as user-follower relations have already been retrieved, this will populate the table **SharedFollowers** with the union size, intersection size, and Jaccard index of any two users' sets of followers (as long as the size of the union is greater than 0).
Similarly, `python calculate_sharedfriends.py DATABASE.db` will populate **SharedFriends**.

Updating Retweet and Favorite Counts
=
Given a SQLite3 database populated with Tweets as created by the Streaming or Searching scripts described below, this script updates the retweet and favorite count for each tweet.  If the tweet data cannot be found, the values will not be changed.  To run the script, run the command `python update_tweets.py config/tweetids.txt DATABASE.db`, where **DATABASE.db** is the SQLite3 database.

For more reference, visit the [Twitter Search API](https://dev.twitter.com/rest/public/search) or the [Twitter Streaming API](https://dev.twitter.com/streaming/public).
