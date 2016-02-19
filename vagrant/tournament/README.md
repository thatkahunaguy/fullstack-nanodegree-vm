# [Tournament Planner Project](https://www.udacity.com/course/viewer#!/c-ud197-nd/l-3521918727/m-3519689284)

This project is a python module using a PostgreSQL database which can track players, matches, and tournaments and utilizes a Swiss system to suggest player pairings for future rounds.  The module prevents rematches, utilizes Opponent Match Wins(OMW) for ranking players with an equal number of wins, and can accomodate ties, odd numbers of players, and multiple tournaments per the extra credit notes.  The project contains a test suite which was modified to test these additional features.



## Table of contents

* [Quick start](#quick-start)
* [Bugs and feature requests](#bugs-and-feature-requests)
* [Documentation](#documentation)
* [Contributing](#contributing)
* [Community](#community)
* [Versioning](#versioning)
* [Creators](#creators)
* [Copyright and license](#copyright-and-license)


## Quick start

To get started:

* Clone the repo: `git clone https://github.com/thatkahunaguy/fullstack-nanodegree-vm/tree/master/vagrant/tournament`.
* This project requires python 2.7
* The python modules are described below
* To run the test suite, execute python tournament_test.py

### What's included

Within the download you'll find the following directories and files. You'll see the folowing:

```
tournament/
├── mwmatching.py       *graph theory maxweight matching algorithm by Joris van Rantwijk*
├── populate.py         *test file with various player & tournament dbase populations*
├── tournament.py       *main python modules for tournament management*
├── tournament.sql      *tournament dbase schema & views*
├── tournament_test.py  *python test execution for tournament.py*
├── README.md
```



## Bugs and feature requests
Note that the ranking alogrithm was implemented as requested in the assignment using match wins followed by OMW to rank players.  With ties incorporated, this ranking methodology can result in ties being worse than losses for a player.  For example, if a tournament has 2 matches, one a tie and the other a win, the 2 players with the tie will be ranked in 3rd and last place which doesn't makes sense.  This because they have 0 wins just like the player with the loss but also have an OMW of 0 while the "loser" in 2nd has an OMW of 1.  The fix is to simply incorporate ties in the player ranking but because it requires refactoring and it's time to move on to bigger and better things I didn't address this.

## Documentation

Functions in **Tournament.py** are outlined below.  More detail on function inputs & outputs can be found in the code comments.

##### registerPlayer(name)

Adds a player to the league so that they may be registered for tournaments.

##### countPlayers()

Returns the number of currently registered players.

##### deletePlayers()

Clear out all the player records from the database.


##### createTournament(name)

Adds a tournament to the league.

##### deleteTournaments()

Clear out all the player records from the database.

##### registerTournamentPlayer(tournament, player)

Adds a player to a specific tournament.

##### reportMatch(tournament, winner, *loser opt, tie = TRUE opt*)

Stores the outcome of a single match between two players in the database.  If loser is not included a bye is reported.  If the match is a tie, tie = TRUE must be set.

##### deleteMatches()
Clear out all the match records from the database.

##### playerStandings(*tournament opt*)
Returns a list of (id, name, wins, matches) for each player, sorted by the number of wins and then the Opponent Match Wins each player has.  This is for the full league unless a tournament is specified.

##### opponents(tournament, player)
Returns a list of opponents a player has played against.

##### opponent_Match_Wins(tournament, player)
Returns the OMW value for a player which is the number of wins all of the player's opponents have accumulated.

##### whoHadABye(tournament)
Returns a list of players who have had a bye in a tournament.

##### weights(standings, tournament)
Returns a list of edges & weights for a graph based on the standings [i, j, weight].  Weights are high (10000) to prevent rematches if players have played and otherwise a function(win differential, rank differential).  Win differential is 10x weighted since we want players with equivalent wins but differing rank to play prior to players with differing win values.

    *f(win_diff, rank_diff) = 10 * win_diff + rank_diff*

This graph is then used in a minimum weight, maximum match function via mwmatching.py  As noted in the bugs/features section, ties and losses are equivalent for this algorithm since the ranking was requested based on wins only.  See the [Contributing](##Contributing) section below for references.

##### swissPairings(tournament)

Given the existing set of registered players and the matches they have played, generates and returns a list of pairings according to the Swiss system. Each pairing is a tuple (id1, name1, id2, name2), giving the ID and name of the paired players. If there are an odd number of players, it assigns a bye and returns pairings for the remaining, even group of players.  For instance, if there are nine registered players, this function returns four pairings. 

## Contributing

The algorithm to pair and ensure no rematches was modeled on [Leaguevine](https://www.leaguevine.com/blog/18/swiss-tournament-scheduling-leaguevines-new-algorithm/) with modifications to weighting to make it a function of win & rank difference. 

The minimum weight maximum match algorithm was implemented based on work in [Healthy Algorithms](http://healthyalgorithms.com/2009/03/23/aco-in-python-minimum-weight-perfect-matchings-aka-matching-algorithms-and-reproductive-health-part-4/).

The actual maximum weight matching algorithm code used is by [Joris van Rantwijk](http://jorisvr.nl/maximummatching.html). 

## Community

* Udacity discussions are [here](https://discussions.udacity.com/c/nd004-p2-tournament-results).


## Versioning

Debut release

## Creators

**John Glancy**

* <https://github.com/thatkahunaguy>

**Udacity**
* <https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004>

## Copyright and license

Code released under [the MIT license](https://opensource.org/licenses/MIT). Docs released under [Creative Commons](http://creativecommons.org/licenses/by/4.0/).


