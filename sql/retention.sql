-- UTC exact-day retention; immature observations are NULL, not zero.
WITH days(day_n) AS (VALUES (1),(7),(30)),
activity AS (SELECT DISTINCT user_id,event_date FROM events
            WHERE event_name='session' AND event_date<=:as_of)
SELECT u.install_date,d.day_n,COUNT(*) AS cohort_size,
 CASE WHEN date(u.install_date,'+'||d.day_n||' days')<=:as_of
 THEN COUNT(a.user_id) END AS retained,
 CASE WHEN date(u.install_date,'+'||d.day_n||' days')<=:as_of
 THEN COUNT(a.user_id)*1.0/COUNT(*) END AS retention
FROM users u CROSS JOIN days d
LEFT JOIN activity a ON a.user_id=u.user_id
 AND a.event_date=date(u.install_date,'+'||d.day_n||' days')
WHERE u.install_date<=:as_of
GROUP BY u.install_date,d.day_n ORDER BY u.install_date,d.day_n;
