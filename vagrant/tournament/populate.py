#!/usr/bin/env python
# 
# populate the database for testing
#

import psycopg2

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")



conn = connect()
c = conn.cursor()
c.execute("INSERT INTO players (player_name) values ('Joe Blow');")
c.execute("INSERT INTO players (player_name) values ('Daisy Duke');")
c.execute("INSERT INTO matches (player1_id, player2_id, round) values (1,2,1);")
conn.commit() 
conn.close()