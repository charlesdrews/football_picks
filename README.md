football_picks
==============

This script makes football picks based on each team's YTD points scored
and points allowed. It retrieve the current week's schedule and YTD team
stats from ESPN.com as html, parses the html, then make picks using an
extremely simple calculation. Finally, it prints the picks to stdout
along with the team names and stats used for each matchup, sorted by
away team name.

The algorithm for predicting scores is very simple and naive. It is based
only on average points scored and average points allowed. It is not
intended to be sophisticated, only to automate a simple process I
previously performed manually.
