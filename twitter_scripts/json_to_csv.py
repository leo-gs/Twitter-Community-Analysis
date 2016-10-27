import csv
import json
import sys

screenname_dict = json.load(open(sys.argv[1]))

writer = csv.writer(open(sys.argv[1].split('.')[0] + '.csv', 'w+'))

for screenname, relations in screenname_dict.items():
	writer.writerow([screenname, ','.join(map(str, relations))])
