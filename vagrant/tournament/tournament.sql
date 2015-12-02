-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
-- delete the tournament database if it already exists
DROP DATABASE IF EXISTS tournament;

CREATE DATABASE tournament;

-- is this psql connect command something which is included generally?
\c tournament;

CREATE TABLE players (
    player_id serial PRIMARY KEY, 
    player_name text);
    
-- Might be able to make primary key below a combo foreign of round & players?
CREATE TABLE matches (
     match_id serial PRIMARY KEY,
     round integer,
     player1_id integer REFERENCES players(player_id), 
     player2_id integer REFERENCES players(player_id),
     winner_id integer REFERENCES players(player_id))
--     tournament_id integer REFERENCES tournaments,

-- initial table design to add additional tournaments in future
-- CREATE TABLE tournaments (
--     tournament_id serial PRIMARY KEY, 
--     tournament_name text);
--
-- CREATE TABLE tournament_registrations (
--     tournament_id integer REFERENCES tournaments, 
--     player_id integer REFERENCES players);
