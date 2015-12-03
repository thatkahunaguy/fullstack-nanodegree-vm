#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")
    
# decided to do this in the initial tournament.sql database setup instead
# need to understand better pros/cons of doing it in initialization vs
# python code - within these functions doesn't seem the best place?
# def create_views():
#     """Create views for the win & loss record and matches played."""
#     # action: office hours to figure out if I should do this in Python
#     # or upon database setup since with the current function setup the
#     # program will try to recreate the views every time functions are called
#     conn = connect()
#     c = conn.cursor()
#     c.execute('''
#     CREATE VIEW win_record AS
#     SELECT players.player_id AS player, players.player_name, count(matches.winner_id) AS wins
#     FROM players LEFT JOIN matches
#         ON players.player_id = matches.winner_id
#     GROUP BY player;''')
#     c.execute('''
#     CREATE VIEW loss_record AS
#     SELECT players.player_id AS player, count(matches.winner_id) AS losses
#     FROM players LEFT JOIN matches
#         ON (players.player_id != matches.winner_id) AND
#            ((players.player_id = matches.player1_id) OR
#            (players.player_id = matches.player2_id))
#     GROUP BY player;''')
#     c.execute('''
#     CREATE VIEW matches_played AS
#     SELECT players.player_id AS player, count(matches.match_id) AS matches
#     FROM players LEFT JOIN matches
#         ON (players.player_id = matches.player1_id) OR
#            (players.player_id = matches.player2_id)
#     GROUP BY player;''')
#     conn.commit() 
#     conn.close()


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM matches;")
    conn.commit() 
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM players;")
    conn.commit() 
    conn.close()

def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT count(player_id) FROM players;")
    count = c.fetchone()[0]
    # debug line to delete
    print "Player count is: {}".format(count)
    conn.close()
    return count

def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO players (player_name) values ('{}');".format(name))
    conn.commit() 
    conn.close()
    

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    standings = ()
    conn = connect()
    c = conn.cursor()
    # create views of win_record, loss_record, & matches_played
    # create_views()  - dropped since I added to initial sql file
    # action: set up office hours to discuss when a select column must be 
    # aggregated or GROUP BY
    c.execute('''
        SELECT win_record.player, win_record.player_name, win_record.wins as wins,  
               matches_played.matches
        FROM win_record 
            JOIN loss_record ON win_record.player = loss_record.player
            JOIN matches_played ON win_record.player = matches_played.player
        ORDER BY wins DESC;''')
    standings = c.fetchall(); 
    conn.close()
    return standings

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
 
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """


