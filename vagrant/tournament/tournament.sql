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
CREATE TYPE outcome AS ENUM ('win', 'loss', 'tie', 'bye', 'default');

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
 
 CREATE TABLE match_participants (
     match_id integer REFERENCES matches,
     player_id integer REFERENCES players,
     match_result outcome);   


-- Create views for win_record, loss_record, & matches played
-- action: investigate whether this can be refactored into fewer views

CREATE VIEW win_record AS
    SELECT player_id AS player, count(match_result) AS wins 
    FROM match_participants          
    WHERE match_result = 'win'  OR match_result = 'bye'
    GROUP BY player
    ORDER BY wins DESC;
    
CREATE VIEW loss_record AS
    SELECT player_id AS player, count(match_result) AS losses 
    FROM match_participants          
    WHERE match_result = 'loss'
    GROUP BY player
    ORDER BY losses DESC;

CREATE VIEW tie_record AS
    SELECT player_id AS player, count(match_result) AS ties 
    FROM match_participants          
    WHERE match_result = 'tie'
    GROUP BY player
    ORDER BY ties DESC;

-- might need to change this if we don't want to count defaults & byes as matches
CREATE VIEW matches_played AS
    SELECT player_id AS player, count(match_result) AS matches
    FROM match_participants           
    GROUP BY player;
    
--  refactor investigation
-- http://stackoverflow.com/questions/28436384/sql-counting-wins-and-losses
-- select
--     season, team,
--     count(case when outcome = 'W' then 1 else null end) as wins,
--     count(case when outcome = 'L' then 1 else null end) as losses
-- from
--     (
--     select season, winning_team as team, 'W' as outcome from cbb.regular_season union all
--     select season, losing_team as team, 'L' as outcome from cbb.regular_season
--     ) as games
-- group by season, team
--
-- need to add tournament functionality here
CREATE VIEW standings AS
    SELECT
        player_id,
        count(case when match_result = 'win' then 1 else NULL end) as wins,
        count(case when match_result = 'loss' then 1 else NULL end) as losses,
        count(case when match_result = 'tie' then 1 else NULL end) as ties,
        count(match_result) as matches_played
    FROM match_participants
    GROUP BY player_id
    ORDER BY wins DESC;
        


CREATE VIEW match_record AS
    SELECT players.player_id, players.player_name, win_record.wins as wins,  
           loss_record.losses, tie_record.ties, matches_played.matches
    FROM players 
        LEFT JOIN win_record ON players.player_id = win_record.player
        LEFT JOIN loss_record ON players.player_id = loss_record.player
        LEFT JOIN tie_record ON players.player_id = tie_record.player
        LEFT JOIN matches_played ON players.player_id = matches_played.player
    ORDER BY wins DESC;