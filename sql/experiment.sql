-- Intent-to-treat: every assigned eligible user remains in the denominator.
SELECT u.variant,COUNT(DISTINCT u.user_id) AS n,
 COUNT(DISTINCT CASE WHEN e.event_id IS NOT NULL THEN u.user_id END) AS successes
FROM users u LEFT JOIN events e ON e.user_id=u.user_id
 AND e.event_name='tutorial_complete' AND e.event_date=u.install_date
WHERE u.install_date<=:as_of
GROUP BY u.variant ORDER BY u.variant;
