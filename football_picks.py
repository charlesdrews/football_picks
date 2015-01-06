#!/usr/bin/python
"""Football Picks

This script makes football picks based on each team's YTD points scored
and points allowed. It retrieve the current week's schedule and YTD team
stats from ESPN.com as html, parses the html, then make picks using an
extremely simple calculation. Finally, it prints the picks to stdout
along with the team names and stats used for each matchup, sorted by
away team name.
"""

import urllib2
import re

def main():
    """Predict winners of this week's NFL games & print to stdout."""
    schedule_url, offense_stats_url, defense_stats_url = define_urls()
    schedule = parse_schedule(schedule_url)
    offense_stats = parse_offense_stats(offense_stats_url)
    defense_stats = parse_defense_stats(defense_stats_url)
    predict_winners(schedule, offense_stats, defense_stats)
    exit(0)

def define_urls():
    """Specify the URLs for the html that needs to be parsed."""
    schedule_url = "http://espn.go.com/nfl/schedule"
    offense_stats_url = "http://espn.go.com/nfl/statistics/team/_/stat/total" \
                        "/seasontype/2"
    defense_stats_url = "http://espn.go.com/nfl/statistics/team/_/stat/total" \
                        "/position/defense/seasontype/2"
    return schedule_url, offense_stats_url, defense_stats_url

def parse_schedule(schedule_url):
    """Read & parse schedule html, then save pairings in dictionary."""
    schedule = {}
    for line in urllib2.urlopen(schedule_url):
        if (" at " in line
                and "Sports Authority Field at Mile High" not in line
                and "ESPN.com" not in line):
            # Presense of "at" indicates line displays a matchup,
            # unless it's one of 2 special cases
            line = re.sub(r"<[^<>]+>", "", line)  # remove html tags
            line = re.sub(r" at ", ",", line)     # replace " at " w/ ,
            line = re.sub(r"\n$", "", line)       # remove trailing newline
            line = line.split(",")
            if line[0] != "TBD" and line[1] != "TBD":
                # Record matchup if it's not a TBD
                schedule[line[0]] = line[1]
    return schedule

def parse_offense_stats(offense_stats_url):
    """Read & parse offensive stats html, then save in dictionary."""
    offense_stats = {}
    for line in urllib2.urlopen(offense_stats_url):
        if re.search(r"RK.*TEAM.*YDS", line):
            # Look for the line of html containing the stat table headers.
            line = re.sub(r"<\/tr>", "@", line)     # mark table line breaks
            line = re.sub(r"<[^<>]+>", " ", line)   # remove other html tags
            line = re.sub(r"( ){2,}", ",", line)    # replace mult. spaces w/ ,
            line = re.sub(r",@,", "\n", line)       # replace @ w/ newline
            line = re.sub(r" @,", "\n", line)       # ditto
            line = re.sub(r"^.*PTS/G\n", "", line)  # remove row w/ col. names
            line = re.sub(r" @$", "", line)         # remove trailing @
            for new_line in line.splitlines():      # split at the added \n
                new_line = new_line.split(",")
                offense_stats[new_line[1]] = float(new_line[9])
    return offense_stats

def parse_defense_stats(defense_stats_url):
    """Read & parse defensive stats html, then save in dictionary."""
    defense_stats = {}
    for line in urllib2.urlopen(defense_stats_url):
        if re.search(r"RK.*TEAM.*YDS", line):
            # Look for the line of html containing the stat table headers.
            line = re.sub(r"<\/tr>", "@", line)     # mark table line breaks
            line = re.sub(r"<[^<>]+>", " ", line)   # remove other html tags
            line = re.sub(r"( ){2,}", ",", line)    # replace mult. spaces w/ ,
            line = re.sub(r",@,", "\n", line)       # replace @ w/ newline
            line = re.sub(r" @,", "\n", line)       # ditto
            line = re.sub(r"^.*PTS/G\n", "", line)  # remove row w/ col. names
            line = re.sub(r" @$", "", line)         # remove trailing @
            for new_line in line.splitlines():      # split at the added \n
                new_line = new_line.split(",")
                defense_stats[new_line[1]] = float(new_line[9])
    return defense_stats

def predict_winners(schedule, offense_stats, defense_stats):
    """Predict winner for each matchup, including margin of victory."""
    keys = schedule.keys()
    keys.sort()
    for key in keys:
        away_team = key
        home_team = schedule[key]
        try:
            off_pts_1 = offense_stats[away_team]
            off_pts_2 = offense_stats[home_team]
        except KeyError, e:
            print "\nKey %s not found in dictionary offense_stats" % str(e)
            print "Check the offense_stats_url value\n"
            return
        try:
            def_pts_1 = defense_stats[away_team]
            def_pts_2 = defense_stats[home_team]
        except KeyError, e:
            print "\nKey %s not found in dictionary defense_stats" % str(e)
            print "Check the defense_stats_url value\n"
            return
        print (away_team + ' (' + str(off_pts_1) + ', ' + str(def_pts_1) + ') at '
                + home_team + ' (' + str(off_pts_2) + ', ' + str(def_pts_2) + ')')
        outcome = off_pts_1 - off_pts_2 + def_pts_2 - def_pts_1
        if outcome < 0:
            # If outcome is negative, then home_team is picked
            winner = home_team
            margin = outcome * -1
        else:
            winner = away_team
            margin = outcome
        print '    pick: ' + winner + ' by ' + str(margin) + '\n'

if __name__ == "__main__":
    main()
