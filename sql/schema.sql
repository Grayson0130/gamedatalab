PRAGMA foreign_keys = ON;
CREATE TABLE users (
 user_id TEXT PRIMARY KEY, install_date TEXT NOT NULL,
 channel TEXT NOT NULL CHECK(channel IN ('organic','search','creator')),
 variant TEXT NOT NULL CHECK(variant IN ('control','treatment'))
);
CREATE TABLE events (
 event_id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(user_id),
 event_date TEXT NOT NULL,
 event_name TEXT NOT NULL CHECK(event_name IN ('session','tutorial_complete','purchase','refund')),
 revenue_cents INTEGER NOT NULL,
 CHECK((event_name='purchase' AND revenue_cents>0) OR
       (event_name='refund' AND revenue_cents<0) OR
       (event_name IN ('session','tutorial_complete') AND revenue_cents=0))
);
CREATE INDEX events_user_date ON events(user_id,event_date);
CREATE TABLE acquisition_costs (
 user_id TEXT PRIMARY KEY REFERENCES users(user_id), cost_cents INTEGER NOT NULL CHECK(cost_cents>=0)
);
