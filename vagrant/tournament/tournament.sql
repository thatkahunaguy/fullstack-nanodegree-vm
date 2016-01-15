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

-- create an enumerated type for the match outcomes
CREATE TYPE outcome AS ENUM ('win', 'loss', 'tie', 'bye');

CREATE TABLE players (
    player_id serial PRIMARY KEY, 
    player_name text);

-- Initial table design to add additional tournaments
CREATE TABLE tournaments (
    tournament_id serial PRIMARY KEY, 
    tournament_name text);
    
CREATE TABLE tournament_registrations (
    tournament_id integer REFERENCES tournaments, 
    player_id integer REFERENCES players);
    
CREATE TABLE matches (
     match_id serial PRIMARY KEY,
     tournament_id integer REFERENCES tournaments,
     round integer);
 
-- probably need to update player_id to reference tournament registrations
-- to validate it is a registered player (how to access correct tournament?)
 CREATE TABLE match_results (
     match_id integer REFERENCES matches,
     player_id integer REFERENCES players,
     match_result outcome);   


-- this is the specific view requested by the assignment, wins only
-- (may need matches played to delete byes & defaults)
CREATE VIEW standings AS
    SELECT
        matches.tournament_id as tournament_id,
        players.player_id as player,
        players.player_name as player_name,
        count(case when match_results.match_result = 'win' then 1 else NULL end) as wins,
        count(case when match_results.match_result != 'bye' then 1 else NULL end) 
            as matches_played
    FROM players 
        LEFT JOIN match_results
            ON players.player_id = match_results.player_id
        LEFT JOIN matches
            ON match_results.match_id = matches.match_id
    GROUP BY tournament_id, player
    ORDER BY wins DESC;

-- this view includes losses and ties (may need matches played to delete byes & defaults)
CREATE VIEW match_record AS
    SELECT
        players.player_id as player,
        count(case when match_results.match_result = 'win' then 1 else NULL end) as wins,
        count(case when match_results.match_result = 'loss' then 1 else NULL end) as losses,
        count(case when match_results.match_result = 'tie' then 1 else NULL end) as ties,
        count(case when match_results.match_result = 'bye' then 1 else NULL end) as byes,
        count(case when match_results.match_result != 'bye' then 1 else NULL end) 
            as matches_played
    FROM players LEFT JOIN match_results
    ON players.player_id = match_results.player_id
    GROUP BY player
    ORDER BY wins DESC;


        