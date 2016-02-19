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
-- could add defaults in future as an example
CREATE TYPE outcome AS ENUM ('win', 'loss', 'tie', 'bye');

CREATE TABLE players (
    player_id serial PRIMARY KEY, 
    player_name text);

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
 
-- CHORE: probably need to update player_id to reference tournament registrations
-- to validate it is a registered player (how to access correct tournament?)
CREATE TABLE match_results (
     match_id integer REFERENCES matches,
     player_id integer REFERENCES players,
     match_result outcome);   

-- this is the specific view requested by the assignment, wins only
-- byes DO NOT provide a win
-- byes DO NOT count as a match played
-- The above are easy to modify or could be assigned settings variables if desired
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
    ORDER BY tournament_id, wins DESC;


-- this view is a list of all match opponents - should assess whether the single
-- player entry match results table was the right design vs entering player & opponent
-- which wouldn't require this view.  Originally done single line so I could accomodate
-- more than just byes in the future...for example, defaults, injury retirements etc.
CREATE VIEW opponents AS
    SELECT matches.tournament_id, a.player_id as player, b.player_id as opponent
    FROM match_results a
        INNER JOIN match_results b
            ON (a.match_id = b.match_id) and (a.player_id != b.player_id)
        LEFT JOIN matches
           ON a.match_id = matches.match_id;    

-- opponent match wins
CREATE VIEW opponent_match_wins AS
    SELECT opponents.tournament_id, opponents.player as player_1, sum(wins) as OMW
    FROM opponents LEFT JOIN standings
    ON (opponents.opponent = standings.player)
        and (opponents.tournament_id = standings.tournament_id)
    GROUP BY opponents.tournament_id, player_1;
    
-- this view includes losses and ties (may need matches played to delete byes & defaults)
-- it's not currently used but would be the view used if losses, ties, & byes needed to
-- be passed.  The assignment specifies that only wins & matches are to be used and I
-- didn't feel the need to update queries to use this view...time to move on.
CREATE VIEW match_record AS
    SELECT
        matches.tournament_id as tournament_id,
        players.player_id as player,
        count(case when match_results.match_result = 'win' then 1 else NULL end) as wins,
        count(case when match_results.match_result = 'loss' then 1 else NULL end) as losses,
        count(case when match_results.match_result = 'tie' then 1 else NULL end) as ties,
        count(case when match_results.match_result = 'bye' then 1 else NULL end) as byes,
        count(case when match_results.match_result != 'bye' then 1 else NULL end) 
            as matches_played
    FROM players 
        LEFT JOIN match_results
            ON players.player_id = match_results.player_id
        LEFT JOIN matches
            ON match_results.match_id = matches.match_id
    GROUP BY matches.tournament_id, player
    ORDER BY matches.tournament_id, wins DESC;

CREATE VIEW omw_record AS
    SELECT m.tournament_id, m.player, m.player_name, m.wins, m.matches_played, o.omw
    FROM standings AS m
        LEFT JOIN opponent_match_wins AS o
            ON (m.tournament_id = o.tournament_id)
                AND (m.player = o.player_1)
    ORDER BY m.tournament_id, wins DESC, omw DESC;       
        
    
        