import csv
import json

INPUT_FILENAME = 'data/screennames.csv'
OUTPUT_FILENAME = 'data/screenname_to_user_id.json'

screenname_to_user_id = {}

reader = csv.reader(open(INPUT_FILENAME))

for row in reader:
	screenname = row[0]
	user_id = row[1]
	screenname_to_user_id[screenname] = user_id

json.dump(screenname_to_user_id, open(OUTPUT_FILENAME, 'w+'))