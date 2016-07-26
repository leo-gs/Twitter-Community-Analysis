import csv
import json
import sys

username_dict = json.load(open(sys.argv[1]))

writer = csv.writer(open(sys.argv[1].split('.')[0] + '.csv', 'w+'))

for username, relations in username_dict.items():
	writer.writerow([username, ','.join(map(str, relations))])
