-- Tables the radar expects. In production these would come from the fleet
-- telemetry store (weekly_activity) and the CRM (accounts, sites, expansions).

CREATE TABLE accounts (
  account_id   TEXT PRIMARY KEY,
  account_name TEXT,
  industry     TEXT,
  sites_total  INTEGER          -- facilities the customer operates, with or without robots
);

CREATE TABLE sites (
  site_id                     TEXT PRIMARY KEY,
  account_id                  TEXT REFERENCES accounts(account_id),
  task                        TEXT,     -- palletizing, case picking, kitting...
  robots_start                INTEGER,
  similar_lines_without_robot INTEGER,  -- from the site walk or the AE's notes
  scheduled_hours_per_week    INTEGER   -- per robot
);

CREATE TABLE weekly_activity (
  site_id            TEXT REFERENCES sites(site_id),
  week               INTEGER,
  robots             INTEGER,
  scheduled_hours    REAL,   -- hours the customer booked
  billed_hours       REAL,   -- hours the robots actually worked
  uptime             REAL,
  tutor_assist_share REAL,   -- share of picks that needed a remote tutor
  sku_changeovers    INTEGER,
  PRIMARY KEY (site_id, week)
);

CREATE TABLE expansions (
  site_id      TEXT REFERENCES sites(site_id),
  week         INTEGER,
  robots_added INTEGER
);
