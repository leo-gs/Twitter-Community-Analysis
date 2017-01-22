INSERT INTO SharedFriends
SELECT u.u1id, u.u2id, u.friend_union, i.friend_intersection, (1.0*i.friend_intersection)/u.friend_union
FROM 
	(SELECT u1.user_id AS u1id, u2.user_id AS u2id, COUNT(DISTINCT uf.friend_id) AS friend_union
	FROM User u1, User u2, Userfriend uf
	WHERE u1.user_id != u2.user_id
	AND (uf.user_id = u1.user_id OR uf.user_id = u2.user_id)
	GROUP BY u1.user_id, u2.user_id
	HAVING COUNT(DISTINCT uf.friend_id) > 0) u,

	(SELECT u1.user_id AS u1id, u2.user_id AS u2id, COUNT(*) AS friend_intersection
	FROM User u1, User u2, Userfriend uf1, Userfriend uf2
	WHERE u1.user_id != u2.user_id
	AND u1.user_id = uf1.user_id
	AND u2.user_id = uf2.user_id
	AND uf1.friend_id = uf2.friend_id
	GROUP BY u1.user_id, u2.user_id) i

WHERE u.u1id = i.u1id
AND u.u2id = i.u2id;