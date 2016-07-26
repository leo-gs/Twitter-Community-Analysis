import csv
import json
import time

uname_to_follower_id = json.load(open('data/username_to_follower_id.json'))
uname_to_friend_id = json.load(open('data/username_to_friend_id.json'))
uname_to_udata = json.load(open('data/username_to_user_data.json'))

collected_unames = []

uname_to_all_ids = {}
for uname in uname_to_udata:

	if uname in uname_to_follower_id.keys() and uname in uname_to_friend_id.keys():
		collected_unames.append(uname)
		uname_to_all_ids[uname] = uname_to_follower_id[uname] + uname_to_friend_id[uname]


def intersection(l1, l2):
	return set(l1) & set(l2)

def union(l1, l2):
	return set(l1) | set(l2)

def write_edges(connection_dict, output_filename, weight_function):
	writer = csv.writer(open(output_filename, 'w+'))

	for index1 in range(len(collected_unames)):
		uname = collected_unames[index1]
		uid = uname_to_udata[uname]['id']
		connection_ids = connection_dict[uname]
		if weight_function(uname) > 0 and len(connection_ids) > 0:
			print output_filename + '\t' + str(index1) + '/' + str(len(collected_unames))

			for index2 in range(index1, len(collected_unames)):
				uname2 = collected_unames[index2]
				uid2 = uname_to_udata[uname2]['id']
				connection_ids2 = connection_dict[uname2]

				if weight_function(uname2) > 0 and len(connection_ids2) > 0:
					# print uname + ', ' + uname2
					x = intersection(connection_ids, connection_ids2)
					X = len(x) * (float(len(connection_ids))/weight_function(uname)) * (float(len(connection_ids2))/weight_function(uname2))
					U = float(weight_function(uname) + weight_function(uname2) - X)
					if X > 0 and X/U > 0.05:
						writer.writerow([uid, uid2, X, U, X/U])

write_edges(uname_to_follower_id, 'data/weights_followers.csv', lambda x: int(uname_to_udata[x]['followers_count']))
write_edges(uname_to_friend_id, 'data/weights_friends.csv', lambda x: int(uname_to_udata[x]['friends_count']))
write_edges(uname_to_all_ids, 'data/weights.csv', lambda x: int(uname_to_udata[x]['followers_count']) + int(uname_to_udata[x]['friends_count']))