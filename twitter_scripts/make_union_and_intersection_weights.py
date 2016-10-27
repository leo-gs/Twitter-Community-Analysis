import csv
import json
import time

sname_to_follower_id = json.load(open('data/screenname_to_follower_id.json'))
sname_to_friend_id = json.load(open('data/screenname_to_friend_id.json'))
sname_to_udata = json.load(open('data/screenname_to_user_data.json'))

collected_snames = []

sname_to_all_ids = {}
for sname in sname_to_udata:

	if sname in sname_to_follower_id.keys() and sname in sname_to_friend_id.keys():
		collected_snames.append(sname)
		sname_to_all_ids[sname] = sname_to_follower_id[sname] + sname_to_friend_id[sname]


def intersection(l1, l2):
	return set(l1) & set(l2)

def union(l1, l2):
	return set(l1) | set(l2)

def write_edges(connection_dict, output_filename, weight_function):
	writer = csv.writer(open(output_filename, 'w+'))

	for index1 in range(len(collected_snames)):
		sname = collected_snames[index1]
		uid = sname_to_udata[sname]['id']
		connection_ids = connection_dict[sname]
		if weight_function(sname) > 0 and len(connection_ids) > 0:
			print output_filename + '\t' + str(index1) + '/' + str(len(collected_snames))

			for index2 in range(index1, len(collected_snames)):
				sname2 = collected_snames[index2]
				uid2 = sname_to_udata[sname2]['id']
				connection_ids2 = connection_dict[sname2]

				if weight_function(sname2) > 0 and len(connection_ids2) > 0:
					# print sname + ', ' + sname2
					x = intersection(connection_ids, connection_ids2)
					X = len(x) * (float(len(connection_ids))/weight_function(sname)) * (float(len(connection_ids2))/weight_function(sname2))
					U = float(weight_function(sname) + weight_function(sname2) - X)
					if X > 0 and X/U > 0.05:
						writer.writerow([uid, uid2, X, U, X/U])

write_edges(sname_to_follower_id, 'data/weights_followers.csv', lambda x: int(sname_to_udata[x]['followers_count']))
write_edges(sname_to_friend_id, 'data/weights_friends.csv', lambda x: int(sname_to_udata[x]['friends_count']))
write_edges(sname_to_all_ids, 'data/weights.csv', lambda x: int(sname_to_udata[x]['followers_count']) + int(sname_to_udata[x]['friends_count']))