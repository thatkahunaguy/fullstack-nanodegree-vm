#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
# bleach is an input sanitization library by Mozilla
import bleach
# Maximum weight matching algorithm code used is by Joris van Rantwijk:
#    http://jorisvr.nl/maximummatching.html 
from mwmatching import maxWeightMatching


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match & tournament records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM match_results;")
    c.execute("DELETE FROM matches;")
    conn.commit() 
    conn.close()

def deleteTournaments():
    """Remove all the tournament records from the database.
       You must run deleteMatches() first to delete match records. """
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM tournament_registrations;")
    c.execute("DELETE FROM tournaments;")
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
    # QUESTION: do I need to explicitly provide ORDER BY or is it ok to to assume
    # order specified in the view will be preserved as I did below?
    if tournament:
        c.execute('''SELECT player, player_name, wins, matches_played FROM omw_record 
            WHERE tournament_id = (%s);''',(tournament,))
    else:
    # show the standings across all tournaments
        c.execute('''SELECT player, player_name, sum(wins) as wins, sum(matches_played)
            FROM omw_record GROUP BY player, player_name ORDER BY wins DESC,
            sum(omw) DESC;''')
    standings = c.fetchall(); 
    conn.close()
    # modify standings 
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
        INSERT INTO match_results (match_id, player_id, tourn_id, match_result )
            values (%s, %s, %s, %s);''',(match, winner, tournament_id, outcome1))
    if loser_if_no_bye:
        c.execute('''
            INSERT INTO match_results (match_id, player_id, tourn_id, match_result )
                values (%s, %s, %s, %s);''',(match, loser_if_no_bye, tournament_id, outcome2))
    conn.commit() 
    conn.close()

def opponentMatchWins(tournament, player):
    """Returns the number of wins of a player's opponents in a tournament
    Args:
      tournament:  the tournament id
      player: the player id of the player 
      PRIOR - opponents:   a list of ids of the opponents of player
      
    Returns:
      The sum total of wins of opponents in tournament
    """
    conn = connect()
    c = conn.cursor()
    c.execute('''
        SELECT OMW
        FROM opponents
        WHERE tournament_id = (%s) and player_1 = (%s); ''',(tournament, player))
    wins = c.fetchone()[0];
    return wins

def opponents(tournament, player):
    """Returns a list of the players who have played player in tournament.
    Args:
      tournament:  the tournament id
      player:  the player whose opponents should be returned
      
    Returns:
      A list of ids of the opponents of player
        id: the player's unique id (assigned by the database)
    """
    matches = opponents = []
    conn = connect()
    c = conn.cursor()
    c.execute('''
        SELECT opponent
        FROM opponents
        WHERE tournament_id = (%s) and player = (%s); ''',(tournament, player))
    opponents = c.fetchall(); 
    conn.close()
    return opponents 

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
    byes = []
    conn = connect()
    c = conn.cursor() 
    c.execute('''
        SELECT player_id
        FROM match_results LEFT JOIN matches
        ON matches.match_id = match_results.match_id
        WHERE tournament_id = (%s) and match_result = 'bye'
        GROUP BY player_id; ''',(tournament,))
    byes = c.fetchall();
    conn.close()
    return byes  

def weights(standings, tournament):
    """"Returns a symmetric edge weight matrix of player matchups for tournament.
        Args:
            standings: 
            tournament:  the tournament id
      
        Returns:
           A list of edges & weights based on the standings [i, j, weight] where:
              i, j: index value to players in the standings [0 = first place]
              w: weight of the edge from player i to player j as defined below
        
        Weighting of each edge is:
            10000(very high) to prevent rematches if players have played
            f(win differential, rank differential) if they haven't played - this
                means the lowest weights will go to players who are ranked very
                closely and with a small win differential.  Win differential is
                weighted larger as we want to pair players with the same number
                of wins but different rankings before players with different win
                numbers.  The precise function used is  10 * win_diff + rank diff 
    """
    edges = []
    num_of_players = len(standings)
    for i in range(num_of_players):
        played = opponents(tournament, standings[i][0])
        # OPT: since this is a symmetric matrix I should be able
        # to optimize and only do half the matrix then mirror
        for j in range(num_of_players):
            if (standings[j][0],) in played:
                edges.append([i, j, 10000])
            elif i != j:
                win_diff = abs(standings[i][2] - standings[j][2])
                rank_diff = abs(i - j)
                edges.append([i, j, win_diff * 10 + rank_diff])
    return edges
            
 
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
        
    Algorithm to pair and ensure no rematches was modeled on Leaguevine:
    https://www.leaguevine.com/blog/18/swiss-tournament-scheduling-leaguevines-new-algorithm/
    with modifications to weighting to make it a function of win & rank difference.
    The minimum weight maximum match algorithm was implemented based on work in:
    http://healthyalgorithms.com/2009/03/23/aco-in-python-minimum-weight-perfect-matchings-aka-matching-algorithms-and-reproductive-health-part-4/
    And the actual maximum weight matching algorithm code used is by Joris van Rantwijk:
    http://jorisvr.nl/maximummatching.html 
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
            reportMatch(tournament, bye_id, 0)
            # remove this player from the standings tuple
            standings = tuple(x for x in standings if x[0] != bye_id)
        else:
            # assign the bye to the lowest player who hasn't had one
            bye_id = -1
            while bye_id < 0:
                if ((standings[player][0],) in byes):
                    player -= 1
                    # condition below should never be reached as rounds < players
                    if player == -1: bye_id = standings[0][0];
                else:
                    bye_id = standings[player][0]
                    # record a bye for this player
                    reportMatch(tournament, bye_id, 0)
                    # remove this player from the standings tuple
                    standings = tuple(x for x in standings if x[0] != bye_id)
    # standing will now have an even number of players
    # use minimum weight maximum match graph theory algorithm
    # to assign Swiss Pairings and avoid rematches(due to high rematch weight)
    """ Minimum weight maximum matching algorithm and modifications from
        http://healthyalgorithms.com/2009/03/23/aco-in-python-minimum-weight-perfect-matchings-aka-matching-algorithms-and-reproductive-health-part-4/
    """        
    edges = weights(standings, tournament) 
    # neg weights in max weight match algorithm gives min weights
    neg_edges = [(i, j, -wt) for i, j, wt in edges]
    # use the graph neg_edges in the max weight algorithm to get assignments
    assignments = maxWeightMatching(neg_edges, maxcardinality=True)
    for i in range(len(assignments)):
        player_2 = assignments[i]
        # skip 2nd assignment element in the edge node pair - since all pair
        # elements are repeated the lower index element has already been assigned
        if player_2 > i:
            pairs.append((standings[i][0], standings[i][1],
                    standings[player_2][0], standings[player_2][1]))      
    return pairs
     
    conn.close()


