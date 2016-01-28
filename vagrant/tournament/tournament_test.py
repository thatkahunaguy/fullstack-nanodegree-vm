#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *
from populate import populate

def testDeleteMatches():
    deleteMatches()
    print "1. Old matches can be deleted."


def testDelete():
    deleteMatches()
    deletePlayers()
    print "2. Player records can be deleted."


def testCount():
# added a test of actual count = 2 players via populate.py
    populate();
    c = countPlayers()
    if c == '2':
        raise TypeError(
            "countPlayers() should return numeric two, not string '2'.")
    if c != 2:
        raise ValueError("Initially, countPlayers should return two.")
    print "3a. Initially, countPlayers() returns two."
    deleteMatches()
    deletePlayers()
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3b. After deleting, countPlayers() returns zero."


def testRegister():
    deleteMatches()
    deletePlayers()
    registerPlayer("Chandra Nalaar")
    c = countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDelete():
    deleteMatches()
    deletePlayers()
    registerPlayer("Markov Chaney")
    registerPlayer("Joe Malik")
    registerPlayer("Mao Tsu-hsi")
    registerPlayer("Atlanta Hope")
    c = countPlayers()
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayers()
    c = countPlayers()
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Melpomene Murray")
    registerPlayer("Randy Schwartz")
    # prior to registering for tournaments standings must be for all tournaments
    standings = playerStandings()
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."


def testReportMatches():
    deleteMatches()
    deletePlayers()
    # MODIFIED TO CREATE A TOURNAMENT
    tournament = createTournament("US Open")
    # END MOD
    registerPlayer("Bruno Walton")
    registerPlayer("Boots O'Neal")
    registerPlayer("Cathy Burton")
    registerPlayer("Diane Grant")
    # prior to registering for tournaments standings must be for all tournaments
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    # MODIFIED TO REGISTER PLAYERS TO THE TOURNAMENT
    registerTournamentPlayer(tournament, id1)
    registerTournamentPlayer(tournament, id2)
    registerTournamentPlayer(tournament, id3)
    registerTournamentPlayer(tournament, id4)
    # MODIFIED TO ADD TOURNAMENT TO reportMatch    
    reportMatch(tournament, id1, id2)
    reportMatch(tournament, id3, id4)
    # END MOD
    standings = playerStandings(tournament)
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    print "7. After a match, players have updated standings."


def testPairings():
    deleteMatches()
    deletePlayers()
    # MODIFIED TO CREATE A TOURNAMENT
    tournament = createTournament("US Open")
    # END MOD
    registerPlayer("Twilight Sparkle")
    registerPlayer("Fluttershy")
    registerPlayer("Applejack")
    registerPlayer("Pinkie Pie")
    # prior to registering for tournaments standings must be for all tournaments
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    # MODIFIED TO REGISTER PLAYERS TO THE TOURNAMENT
    registerTournamentPlayer(tournament, id1)
    registerTournamentPlayer(tournament, id2)
    registerTournamentPlayer(tournament, id3)
    registerTournamentPlayer(tournament, id4)
    # MODIFIED TO ADD TOURNAMENT TO reportMatch    
    reportMatch(tournament, id1, id2)
    reportMatch(tournament, id3, id4)
    # END MOD
    pairings = swissPairings(tournament)
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."

def testOddPlayers():
    deleteMatches()
    deletePlayers()
    # MODIFIED TO CREATE A TOURNAMENT
    tournament = createTournament("US Open")
    # END MOD
    registerPlayer("Bruno Walton")
    registerPlayer("Boots O'Neal")
    registerPlayer("Cathy Burton")
    registerPlayer("Diane Grant")
    registerPlayer("Joe Blow")
    # prior to registering for tournaments standings must be for all tournaments
    standings = playerStandings()
    [id1, id2, id3, id4, id5] = [row[0] for row in standings]
    # MODIFIED TO REGISTER PLAYERS TO THE TOURNAMENT
    registerTournamentPlayer(tournament, id1)
    registerTournamentPlayer(tournament, id2)
    registerTournamentPlayer(tournament, id3)
    registerTournamentPlayer(tournament, id4)
    registerTournamentPlayer(tournament, id5)
    # MODIFIED TO ADD TOURNAMENT TO reportMatch
    pairings = swissPairings(tournament)
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings    
    reportMatch(tournament, pid1, pid2)
    reportMatch(tournament, pid3, pid4)
    pairings = swissPairings(tournament)
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings    
    reportMatch(tournament, pid1, pid2)
    reportMatch(tournament, pid3, pid4)
    pairings = swissPairings(tournament)
    [(pid1, pname1, pid2, pnam2), (pid3, pname3, pid4, pname4)] = pairings    
    reportMatch(tournament, pid1, pid2)
    reportMatch(tournament, pid3, pid4)
    # END MOD
    standings = playerStandings(tournament)
    [id1, id2, id3, id4, id5] = [row[0] for row in standings]
    for (i, n, w, m) in standings:
        if i in (id1,) and (w != 3 and m != 3):
            raise ValueError("The top player should have 3 wins & matches recorded.")
        elif i in (id2,) and w != 2 and m != 3:
            raise ValueError("The third player should have had a bye & a win")
        elif i in (id3,) and w != 1 and m != 2:
            raise ValueError("The third player should have had a bye & a win")
        elif i in (id4, id5) and w != 0 and m != 2:
            raise ValueError("The lowest 2 players should have had byes & 0 wins")
    print "9. With an odd # of players 3 get byes & others have updated standings."


if __name__ == '__main__':
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    testOddPlayers()
    print "Success!  All tests pass!"


