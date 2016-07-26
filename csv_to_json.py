import csv
import json

INPUT_FILENAME = 'data/usernames.csv'
OUTPUT_FILENAME = 'data/username_to_user_id.json'

username_to_user_id = {}

reader = csv.reader(open(INPUT_FILENAME))

for row in reader:
	username = row.split()[0]
	user_id = row.split()[1]
	username_to_user_id[username] = user_id

json.dump(username_to_user_id, open(OUTPUT_FILENAME, 'w+'))