This uses the Tweepy API, which can be found [here](http://docs.tweepy.org/en/v3.5.0/api.html).

Before Getting Any Friends and Followers:
=
1.) Setup tweepy by navigating to **tweepy** and running the command `python setup.py`.

2.) Get a Twitter API key [here](https://apps.twitter.com/app/new).  Fill in **twitter_scripts/config/twitter_config.txt** with the access keys/tokens/secrets.  Twitter rate limits each key separately, so you can generate multiple access keys and save them in multiple .txt files if you want do multiple things at once.

3.) Put a .csv file with two columns, Twitter screen name and Twitter user id (in that order) in the **twitter_scripts_/data/** directory.  Name the spreadsheet **usernames.csv**.

4.) In the terminal window, navigate to the **twitter_scripts** directory and run the command `python csv_to_json.py`.  This will reformat the .csv file as a .json file.

5.) Run the command `python get_user_data.py config/twitter_config.txt`.  This will pull data about each user on the spreadsheet from Twitter.

Follower and Following Relations
=
- To get follower relations: run the command `python get_followers.py config/twitter_config.txt`.  This will output **data/username_to_follower_id.json** which maps a screen name to a list of follower ids.  The updates printed to the console don't seem to be completely correct, but I haven't had time to fix that.
- To get friend relations: run the command `python get_friends.py config/twitter_config.txt`.  This will output **data/username_to_friend_id.json** in the which maps a screen name to a list of friend ids.
- To reformat these as spreadsheets, run the commands `python json_to_csv.py data/username_to_follower_id.json` and `python json_to_csv.py data/username_to_friend_id.json`.  This will output **data/username_to_follower_id.csv** and **data/username_to_friend_id.csv**.
- These can take a really long time because of rate limiting.

Union and Intersection of Friends and Followers
=
Run the command `python make_union_and_intersection_weights.py`.  This will output three .csv files of the form **screen name 1, screen name 2, |intersection|, |union|,|intersection|/|union|**.
- **data/weights_followers.csv**: shared followers
- **data/weights_friends.csv**: shared friends
- **data/weights.csv**: shared friends and followers