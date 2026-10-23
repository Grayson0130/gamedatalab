-- Features D0..6; prediction D7; label = no session on D7..13.
SELECT u.user_id,u.install_date,
 COUNT(DISTINCT CASE WHEN e.event_date<date(u.install_date,'+7 days')
 THEN e.event_date END) AS active_days_7,
 CASE WHEN COUNT(DISTINCT CASE WHEN e.event_date>=date(u.install_date,'+7 days')
 THEN e.event_date END)=0 THEN 1 ELSE 0 END AS churned
FROM users u LEFT JOIN events e ON e.user_id=u.user_id AND e.event_name='session'
 AND e.event_date BETWEEN u.install_date AND date(u.install_date,'+13 days')
WHERE date(u.install_date,'+13 days')<=:as_of
GROUP BY u.user_id,u.install_date ORDER BY u.install_date,u.user_id;
