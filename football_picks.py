#!/usr/bin/python
"""Football Picks.

This script makes football picks based on each team's YTD points scored and
points allowed. It retrieve the current week's schedule and YTD team stats from
ESPN.com as html, parses the html, then make picks using an extremely simple
calculation. Finally, it prints the picks to stdout along with the team names
and stats used for each matchup, sorted by away team name.
"""

import urllib2
import re

schedule_url = "http://espn.go.com/nfl/schedule"
# URLs for current season YTD stats:
offense_stats_url = "http://espn.go.com/nfl/statistics/team/_/stat/total"
defense_stats_url = "http://espn.go.com/nfl/statistics/team/_/stat/total" \
                    "/position/defense"

# Temporarily use 2013 regular season stats instead of 2014 YTD
#offense_stats_url = "http://espn.go.com/nfl/statistics/team/_/stat/total" \
#                    "/year/2013"
#defense_stats_url = "http://espn.go.com/nfl/statistics/team/_/stat/total" \
#                    "/position/defense/year/2013"
#print 'Using 2013 regular season stats, not 2014 YTD stats:\n'

# Read & parse schedule html, then save pairings in dictionary
schedule = {}
for line in urllib2.urlopen(schedule_url):
    # The presense of " at " in line indicates that line displays a matchup,
    # unless it's one of two special cases.
    if (" at " in line
            and "Sports Authority Field at Mile High" not in line
            and "ESPN.com" not in line):
        line = re.sub(r"<[^<>]+>", "", line)  # remove html tags
        line = re.sub(r" at ", ",", line)     # replace " at " w/ ,
        line = re.sub(r"\n$", "", line)       # remove trailing newline
        line = line.split(",")
        schedule[line[0]] = line[1]

# Read & parse offensive stats html, then save in dictionary
offense_stats = {}
for line in urllib2.urlopen(offense_stats_url):
    # Look for the line of html containing the stat table headers.
    if re.search(r"RK.*TEAM.*YDS", line):
        line = re.sub(r"<\/tr>", "@", line)     # mark table line breaks w/ @
        line = re.sub(r"<[^<>]+>", " ", line)   # remove all other html tags
        line = re.sub(r"( ){2,}", ",", line)    # replace mult. spaces w/ ,
        line = re.sub(r",@,", "\n", line)       # replace @ w/ newline
        line = re.sub(r" @,", "\n", line)       # ditto
        line = re.sub(r"^.*PTS/G\n", "", line)  # remove 1st row w/ col names
        line = re.sub(r" @$", "", line)         # remove trailing @
        for new_line in line.splitlines():      # split at previously added \n
            new_line = new_line.split(",")
            offense_stats[new_line[1]] = float(new_line[9])

# Read & parse offensive stats html, then save in dictionary
defense_stats = {}
for line in urllib2.urlopen(defense_stats_url):
    # Look for the line of html containing the stat table headers.
    if re.search(r"RK.*TEAM.*YDS", line):
        line = re.sub(r"<\/tr>", "@", line)     # mark table line breaks w/ @
        line = re.sub(r"<[^<>]+>", " ", line)   # remove all other html tags
        line = re.sub(r"( ){2,}", ",", line)    # replace mult. spaces w/ ,
        line = re.sub(r",@,", "\n", line)       # replace @ w/ newline
        line = re.sub(r" @,", "\n", line)       # ditto
        line = re.sub(r"^.*PTS/G\n", "", line)  # remove 1st row w/ col names
        line = re.sub(r" @$", "", line)         # remove trailing @
        for new_line in line.splitlines():      # split at previously added \n
            new_line = new_line.split(",")
            defense_stats[new_line[1]] = float(new_line[9])

# Predict winner for each matchup (for each team pairing in schedule).
keys = schedule.keys()
keys.sort()
for key in keys:
    away_team = key
    home_team = schedule[key]
    off_pts_1 = offense_stats[away_team]
    off_pts_2 = offense_stats[home_team]
    def_pts_1 = defense_stats[away_team]
    def_pts_2 = defense_stats[home_team]
    print (away_team + ' (' + str(off_pts_1) + ', ' + str(def_pts_1) + ') at '
            + home_team + ' (' + str(off_pts_2) + ', ' + str(def_pts_2) + ')')
    outcome = off_pts_1 - off_pts_2 + def_pts_2 - def_pts_1
    # If outcome is negative then home_team is picked, else away_team is picked.
    if outcome < 0:
        winner = home_team
        margin = outcome * -1
    else:
        winner = away_team
        margin = outcome
    print '    pick: ' + winner + ' by ' + str(margin) + '\n'

exit(0)
