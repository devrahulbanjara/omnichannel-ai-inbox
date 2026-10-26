-- Runs once, when the Postgres volume is first created.
-- A separate database for tests, so running tests never touches dev data.
CREATE DATABASE inbox_test OWNER inbox;
