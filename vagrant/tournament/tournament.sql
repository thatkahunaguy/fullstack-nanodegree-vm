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


-- Create views for win_record, loss_record, & matches played
-- action: investigate whether this can be refactored into fewer views
CREATE VIEW win_record AS
    SELECT players.player_id AS player, players.player_name, count(matches.winner_id) AS wins
    FROM players LEFT JOIN matches
        ON players.player_id = matches.winner_id
    GROUP BY player;

-- technically not needed by the program as defined
CREATE VIEW loss_record AS
    SELECT players.player_id AS player, count(matches.winner_id) AS losses
    FROM players LEFT JOIN matches
        ON (players.player_id != matches.winner_id) AND
           ((players.player_id = matches.player1_id) OR
           (players.player_id = matches.player2_id))
    GROUP BY player;

CREATE VIEW matches_played AS
    SELECT players.player_id AS player, count(matches.match_id) AS matches
    FROM players LEFT JOIN matches
        ON (players.player_id = matches.player1_id) OR
           (players.player_id = matches.player2_id)
    GROUP BY player;

CREATE VIEW match_record AS
    SELECT win_record.player, win_record.player_name, win_record.wins as wins,  
           matches_played.matches
    FROM win_record 
        JOIN loss_record ON win_record.player = loss_record.player
        JOIN matches_played ON win_record.player = matches_played.player
    ORDER BY wins DESC;