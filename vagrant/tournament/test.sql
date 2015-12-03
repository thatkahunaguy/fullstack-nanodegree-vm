DROP VIEW IF EXISTS win_record;
DROP VIEW IF EXISTS loss_record;
DROP VIEW IF EXISTS matches_played;

CREATE VIEW win_record AS
SELECT players.player_id AS player, players.player_name, count(matches.winner_id) AS wins
FROM players LEFT JOIN matches
    ON players.player_id = matches.winner_id
GROUP BY player;

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

-- verify views work
select * from win_record;
select * from loss_record;
select * from matches_played;


-- action: set up office hours to discuss when a select column must be 
-- aggregated or GROUP BY
SELECT win_record.wins as wins, loss_record.losses, win_record.player, win_record.player_name, 
       matches_played.matches
FROM win_record 
    JOIN loss_record ON win_record.player = loss_record.player
    JOIN matches_played ON win_record.player = matches_played.player
ORDER BY wins DESC;

-- in order class asks for and without losses
SELECT win_record.player, win_record.player_name, win_record.wins as wins,  
       matches_played.matches
FROM win_record 
    JOIN loss_record ON win_record.player = loss_record.player
    JOIN matches_played ON win_record.player = matches_played.player
ORDER BY wins DESC;


-- UPDATE matches SET winner_id = 44 WHERE match_id = 22;