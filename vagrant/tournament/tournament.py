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


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM match_results;")
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


def playerStandings(tournament = 0):
    """Returns a list of the players and their win records, sorted by wins.
    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.
    
    Args:
      tournament:  
        0 => returns standings from all tournaments
        tournament id => returns standings from that specific tournament

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
    # on the specific tournament ACTION REQUIRED
    if tournament:
        c.execute('''SELECT player, player_name, wins, matches_played FROM standings 
            WHERE tournament_id = (%s);''',(tournament,))
    else:
        c.execute("SELECT player, player_name, wins, matches_played FROM standings;")
    standings = c.fetchall(); 
    conn.close()
    return standings

def reportMatch(tournament_id, winner, loser_if_no_bye, tie=False):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won or who has a bye
      loser:  the id number of the player who lost OR 0 to indicate a bye
      tie(opt): boolean set to true if the match was a tie
      
    """
    conn = connect()
    c = conn.cursor()
    # create a match and return the autogenerated matchid for use
    # populating match_results
    c.execute('''
        INSERT INTO matches (tournament_id) values (%s)
             RETURNING match_id;''',(tournament_id,))
    match = c.fetchone()[0]
    # populate match_partipants with correct outcomes
    if tie:
        outcome1 = outcome2 = "tie" 
    elif not loser_if_no_bye:
        outcome1 = "bye"
    else:
        outcome1 = "win"
        outcome2 = "loss"
    c.execute('''
        INSERT INTO match_results (match_id, player_id, match_result )
            values (%s, %s, %s);''',(match, winner, outcome1))
    if loser_if_no_bye:
        c.execute('''
            INSERT INTO match_results (match_id, player_id, match_result )
                values (%s, %s, %s);''',(match, loser_if_no_bye, outcome2))
    conn.commit() 
    conn.close()

# for computing opponent match wins(omw) later
# get matches played: select match_id from match_results where player_id=1;
# get opponents played: select player_id from match_results where player_id<>1
# AND match_id=1;
# get omw: select wins from standings where player_id=2;

def whoHadABye(tournament):
    """Returns a list of the players who had a bye.
    Args:
      tournament:  the tournament id
      
    Returns:
      A list of ids who have had byes:
        id: the player's unique id (assigned by the database)
        
    Byes in this program show a bye outcome rather
    than simply a "free win" as mentioned in extra credit.
    This allows functionality to identify byes vs. true
    wins if needed.  Byes are not currently counted as 
    wins for standings or as matches played.
    """
    byes = ()
    conn = connect()
    c = conn.cursor() 
    c.execute('''
        SELECT player_id
        FROM match_results LEFT JOIN matches
        ON matches.match_id = match_results.match_id
        WHERE tournament_id = (%s) and match_result = 'bye'
        GROUP BY player_id; ''',(tournament,))
    byes = c.fetchall();
    # DEBUG print 'These folks had a bye ', byes
    # DEBUG print 'Length of byes is ',  len(byes)
    conn.close()
    return byes  

 
def swissPairings(tournament):
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
    
    Args:
      tournament:  the tournament id you want to run swiss pairings on
  
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
    standings = playerStandings()
    # figure out who gets a bye if there are an odd number of players
    num_of_players = len(standings)
    if (num_of_players % 2) > 0:
        # assign a bye to the lowest standing player without a bye
        byes = whoHadABye(tournament)
        player = num_of_players - 1
        if len(byes) == 0:
            # assign the last player if no one has a bye yet
            bye_id = standings[player][0]
            # DEBUG print "Initial bye assigned to: ", bye_id
            reportMatch(tournament, bye_id, 0)
            # remove this player from the standings tuple
            standings = tuple(x for x in standings if x[0] != bye_id)
        else:
            # assign the bye to the lowest player who hasn't had one
            bye_id = -1
            while bye_id < 0:
                if ((standings[player][0],) in byes):
                    player -= 1
                    # condition below should never be reached rounds < players
                    if player == -1: bye_id = standings[0][0];
                else:
                    bye_id = standings[player][0]
                    # record a bye for this player
                    reportMatch(tournament, bye_id, 0)
                    # remove this player from the standings tuple
                    standings = tuple(x for x in standings if x[0] != bye_id)
    # standing will now have an even number of players
    # DEBUG print "Swiss Pair Standings after bye removal:"
    # DEBUG print standings
    for i in range(0, num_of_players - 1, 2):
    # use append since the list is empty & you can't write to an empty element
        pairs.append((standings[i][0], standings[i][1],
                    standings[i+1][0], standings[i+1][1]))
        
    return pairs
     
    conn.close()


