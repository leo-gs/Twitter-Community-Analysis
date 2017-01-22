INSERT INTO SharedFollowers 
SELECT u.u1id, u.u2id, u.follower_union, i.follower_intersection, (1.0*i.follower_intersection)/u.follower_union
FROM 
	(SELECT u1.user_id AS u1id, u2.user_id AS u2id, COUNT(DISTINCT uf.follower_id) AS follower_union
	FROM User u1, User u2, UserFollower uf
	WHERE u1.user_id != u2.user_id
	AND (uf.user_id = u1.user_id OR uf.user_id = u2.user_id)
	GROUP BY u1.user_id, u2.user_id
	HAVING COUNT(DISTINCT uf.follower_id) > 0) u,

	(SELECT u1.user_id AS u1id, u2.user_id AS u2id, COUNT(*) AS follower_intersection
	FROM User u1, User u2, UserFollower uf1, UserFollower uf2
	WHERE u1.user_id != u2.user_id
	AND u1.user_id = uf1.user_id
	AND u2.user_id = uf2.user_id
	AND uf1.follower_id = uf2.follower_id
	GROUP BY u1.user_id, u2.user_id) i

WHERE u.u1id = i.u1id
AND u.u2id = i.u2id;