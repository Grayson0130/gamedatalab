-- Observed receipts/install, D0..DH inclusive. 30% fee is a DEMO assumption.
WITH mature AS (
 SELECT * FROM users WHERE date(install_date,'+'||:horizon||' days')<=:as_of
), revenue AS (
 SELECT u.user_id,COALESCE(SUM(e.revenue_cents),0) AS net_cents
 FROM mature u LEFT JOIN events e ON e.user_id=u.user_id
 AND e.event_date BETWEEN u.install_date AND date(u.install_date,'+'||:horizon||' days')
 GROUP BY u.user_id
)
SELECT u.channel,COUNT(*) AS installs,
 ROUND(SUM(r.net_cents)/100.0,2) AS receipts_usd,
 ROUND(AVG(r.net_cents)/100.0,4) AS observed_receipts_ltv_usd,
 ROUND(AVG(c.cost_cents)/100.0,4) AS cac_usd,
 CASE WHEN SUM(c.cost_cents)>0 THEN SUM(r.net_cents)*0.70/SUM(c.cost_cents) END AS contribution_roas
FROM mature u JOIN revenue r USING(user_id) JOIN acquisition_costs c USING(user_id)
GROUP BY u.channel ORDER BY u.channel;
