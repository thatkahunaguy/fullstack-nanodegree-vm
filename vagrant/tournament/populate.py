#!/usr/bin/env python
# 
# populate the database for testing
#

import psycopg2

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def populate():
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO players (player_name) values ('Joe Blow');")
    c.execute("INSERT INTO players (player_name) values ('Daisy Duke');")
    c.execute("INSERT INTO tournaments (tournament_name) values ('US Open');")
    # get the id of the first player added so matches can be populated
    c.execute("SELECT player_id FROM players WHERE player_name = 'Joe Blow';")
    id = c.fetchone()
    # get the id of the first tournament added so matches can be populated
    c.execute("SELECT tournament_id FROM tournaments WHERE tournament_name = 'US Open';")
    tourney = c.fetchone()
    # register players for the tournament
    c.execute('''INSERT INTO tournament_registrations (player_id)
             values (%s);''',(id[0],))
    c.execute('''INSERT INTO tournament_registrations (player_id)
             values (%s);''',(id[0]+1,))            
    # create a match for the tournament
    c.execute('''INSERT INTO matches (tournament_id, round)
             values (%s, %s);''',(tourney[0], '1'))
    c.execute("SELECT match_id FROM matches WHERE tournament_id = %s;",(tourney[0],))
    match = c.fetchone()
    # register the match winner and loser
    c.execute('''INSERT INTO match_results (match_id, player_id, match_result)
             values (%s, %s, %s);''',(match[0], id[0], 'win'))
    c.execute('''INSERT INTO match_results (match_id, player_id, match_result)
             values (%s, %s, %s);''',(match[0], id[0]+1, 'loss'))
    conn.commit() 
    conn.close()
    
populate()