#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
# bleach is an input sanitization library by Mozilla
import bleach


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

# this will generically delete a table name passed to the function
# kept deleteMatches & deletePlayers in case grading script needs these
def deleteTable(table):
    """Remove all the table records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM (%s);",(table,))
    conn.commit() 
    conn.close()

def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM match_participants;")
    c.execute("DELETE FROM matches;")
    conn.commit() 
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM tournament_registrations;")
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
    # sanitize name input - would this generally be done in these functions or
    # in the functions handling user input?  ie wouldn't I generally design
    # the program so that I santize input in the handler which acquires it from
    # the user rather than in each individual function I might pass input attributes
    # to?
    name = bleach.clean(name)
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO players (player_name) values (%s);",(name,))
    conn.commit() 
    conn.close()

def createTournament(name):
    """Adds a tournament to the tournament database.
  
    The database assigns a unique serial id number for the tournament.  
  
    Args:
      name: the tournament's name (need not be unique).
      
    Returns: the tournament's unique id for immediate use registering players etc.
    """
    # sanitize name input - would this generally be done in these functions or
    # in the functions handling user input?  ie wouldn't I generally design
    # the program so that I santize input in the handler which acquires it from
    # the user rather than in each individual function I might pass input attributes
    # to?
    name = bleach.clean(name)
    conn = connect()
    c = conn.cursor()
    c.execute('''INSERT INTO tournaments (tournament_name) values (%s)
        RETURNING tournament_id;''',(name,))
    tournament = c.fetchone()[0]
    conn.commit() 
    conn.close()
    return(tournament)
    
def registerTournamentPlayer(tournament_id, player_id):
    """Adds a player to a specific tournament's registration
  
    Args:
      player_id: the player's unique player_id from the players table
    """
    conn = connect()
    c = conn.cursor()
    c.execute('''INSERT INTO tournament_registrations (tournament_id, player_id)
        values (%s, %s);''',(tournament_id, player_id,))
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
    # use the standings view - think about whether I need to do a select based
    # on the specific tournament 
    c.execute("SELECT * FROM standings;")
    standings = c.fetchall(); 
    conn.close()
    return standings

def reportMatch(tournament_id, winner, loser, tie=False):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
      tie(opt): boolean set to true if the match was a tie
      
    Note: I decided to make a separate function to handle events
          like byes, defaults etc so the reportMatch function structure
          could stay the same and have minimal impact on test scripts etc
    """
    conn = connect()
    c = conn.cursor()
    # create a match and return the autogenerated matchid for use
    # populating match_participants
    c.execute('''
        INSERT INTO matches (tournament_id) values (%s)
             RETURNING match_id;''',(tournament_id,))
    match = c.fetchone()[0]
    # populate match_partipants with correct outcomes
    if tie:
        outcome1 = outcome2 = "tie" 
    else:
        outcome1 = "win"
        outcome2 = "loss"
    c.execute('''
        INSERT INTO match_participants (match_id, player_id, match_result )
            values (%s, %s, %s);''',(match, winner, outcome1))
    c.execute('''
        INSERT INTO match_participants (match_id, player_id, match_result )
            values (%s, %s, %s);''',(match, loser, outcome2))
    conn.commit() 
    conn.close()

# for computing opponent match wins(omw) later
# get matches played: select match_id from match_participants where player_id=1;
# get opponents played: select player_id from match_participants where player_id<>1
# AND match_id=1;
# get omw: select wins from standings where player_id=2;
  
 
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
    pairs = []
    conn = connect()
    c = conn.cursor()
#     c.execute("SELECT count(player_id) FROM players;")
#     players = c.fetchone()[0]
    standings = playerStandings()
    # assumes an even number of players
    for i in range(0, len(standings) - 1, 2):
    # use append since the list is empty & you can't write to an empty element
        pairs.append((standings[i][0], standings[i][1],
                    standings[i+1][0], standings[i+1][1]))
    return pairs
     
    conn.close()


