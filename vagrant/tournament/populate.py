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
    # get the id of the first player added so matches can be populated
    c.execute("SELECT player_id FROM players WHERE player_name = 'Joe Blow';")
    id = c.fetchone()
    c.execute('''INSERT INTO matches (player1_id, player2_id, round, winner_id)
             values (%s, %s, 1, %s);''',(id[0], id[0]+1, id[0]))
    conn.commit() 
    conn.close()
    
populate()