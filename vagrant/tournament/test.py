import psycopg2

conn = psycopg2.connect("dbname=tournament")
pairs = []
standings = ()
c = conn.cursor()
c.execute("SELECT count(player_id) FROM players;")
players = c.fetchone()[0]
print "# of Players = {}".format(players)
c.execute("SELECT * FROM match_record;")
standings = c.fetchall();
print standings
print "length of standings is ", len(standings)
print "Enter loop"
#assumes an even number of players
for i in range(0, len(standings) - 1, 2):
    print "i = ", i
    pairs.append((standings[i][0], standings[i][1],
                standings[i+1][0], standings[i+1][1]))
print pairs
#     print "pairs[", i, "] = ", pairs[i]
#     print "standings[i] = ", standings[i]
#     for j in range (0, players):
#         print "standings[", i,"][", j, "] = ", standings[i][j]

conn.close()