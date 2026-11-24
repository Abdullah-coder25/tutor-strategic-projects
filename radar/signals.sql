-- Trailing 8-week signals for every site as of week :as_of.
--   utilization    hours worked / hours booked. Above 1 means the robots run past
--                  their booked shifts: the customer is asking for more capacity.
--   overtime_weeks weeks out of 8 where worked hours beat booked hours.
--   avg_uptime     reliability. Nobody expands a robot that keeps stopping.
--   assist_drop    fall in the share of picks needing a remote tutor over the
--                  window. Rising autonomy means better margin on a second robot.
--   changeovers    SKU switches per week. High-mix sites lean on flexible robots.
--   similar_lines  lines in the same plant doing the same task with no robot.
--   open_sites     other facilities the customer runs where Tutor has no robot.
WITH win AS (
  SELECT * FROM weekly_activity WHERE week > :as_of - 8 AND week <= :as_of
),
agg AS (
  SELECT site_id,
         SUM(billed_hours) / SUM(scheduled_hours)                 AS utilization,
         SUM(CASE WHEN billed_hours > scheduled_hours THEN 1 ELSE 0 END) AS overtime_weeks,
         AVG(uptime)                                              AS avg_uptime,
         AVG(sku_changeovers)                                     AS changeovers,
         COUNT(*)                                                 AS weeks_seen
  FROM win GROUP BY site_id
),
first_last AS (
  SELECT site_id,
         MAX(CASE WHEN week = (SELECT MIN(week) FROM win w2 WHERE w2.site_id = win.site_id) THEN tutor_assist_share END)
       - MAX(CASE WHEN week = (SELECT MAX(week) FROM win w2 WHERE w2.site_id = win.site_id) THEN tutor_assist_share END) AS assist_drop
  FROM win GROUP BY site_id
),
site_counts AS (
  SELECT account_id, COUNT(*) AS sites_with_robots FROM sites GROUP BY account_id
)
SELECT s.site_id, s.account_id, a.account_name, a.industry, s.task,
       agg.utilization, agg.overtime_weeks, agg.avg_uptime, fl.assist_drop, agg.changeovers,
       s.similar_lines_without_robot AS similar_lines,
       a.sites_total - sc.sites_with_robots AS open_sites
FROM sites s
JOIN accounts a     ON a.account_id = s.account_id
JOIN agg            ON agg.site_id = s.site_id
JOIN first_last fl  ON fl.site_id = s.site_id
JOIN site_counts sc ON sc.account_id = s.account_id
WHERE agg.weeks_seen = 8;
