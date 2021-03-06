#!/usr/bin/env python

"""Football Picks

This script makes football picks based on each team's YTD points scored
and points allowed. It retrieve the current week's schedule and YTD team
stats from api.fantasydata.net then make picks using an extremely simple
calculation. Finally, it prints the picks to stdout along with the team
names and stats used for each matchup, sorted by away team name.
"""


import sys
import requests
from bs4 import BeautifulSoup


SCHEDULE_URL = 'http://espn.go.com/nfl/schedule'
OFFENSE_STATS_URL = 'http://espn.go.com/nfl/statistics/team/_/stat/total/seasontype/2'
DEFENSE_STATS_URL = 'http://espn.go.com/nfl/statistics/team/_/stat/total/position/defense/seasontype/2'


def main():
    """Predict winners of this week's NFL games & print to stdout."""
    schedule = parse_schedule()
    offense_stats = parse_offense_stats()
    defense_stats = parse_defense_stats()
    predict_winners(schedule, offense_stats, defense_stats)
    sys.exit(0)


def parse_schedule():
    """Read & parse schedule html, then save pairings in dictionary."""
    print 'Retrieving schedule...'
    schedule = {}

    html_response = requests.get(SCHEDULE_URL).text
    soup = BeautifulSoup(html_response, 'html.parser')

    for table in soup.find_all('tbody'):
        for row in table.find_all('tr'):
        #for row in table.find_all('tr', 'has-results'):
            cells = row.find_all('td')
            away_team = get_team_from_cell(cells[0])
            home_team = get_team_from_cell(cells[1])
            schedule[away_team] = home_team

    return schedule


def get_team_from_cell(cell):
    team = cell.select_one('a.team-name').find('span').string
    if team == 'New York':
        if cell.find('abbr').string == 'NYG':
            team = 'NY Giants'
        else:
            team = 'NY Jets'
    elif team == 'Los Angeles':
        if cell.find('abbr').string == 'LAR':
            team = 'LA Rams'
        else:
            team = 'LA Chargers'
    return team


def parse_offense_stats():
    """Read & parse offensive stats html, then save in dictionary."""
    print 'Retrieving offensive stats...'
    offense_stats = {}

    html_response = requests.get(OFFENSE_STATS_URL).text
    soup = BeautifulSoup(html_response, 'html.parser')

    for row in soup.select_one('table.tablehead').select('tr'):
        if row['class'] != ['colhead']:
            cells = row.find_all('td')
            team = cells[1].find('a').string
            points_scored_per_game = cells[9].string
            offense_stats[team] = float(points_scored_per_game)

    return offense_stats


def parse_defense_stats():
    """Read & parse defensive stats html, then save in dictionary."""
    print 'Retrieving defensive stats...'
    defense_stats = {}

    html_response = requests.get(DEFENSE_STATS_URL).text
    soup = BeautifulSoup(html_response, 'html.parser')

    for row in soup.select_one('table.tablehead').select('tr'):
        if row['class'] != ['colhead']:
            cells = row.find_all('td')
            team = cells[1].find('a').string
            points_allowed_per_game = cells[9].string
            defense_stats[team] = float(points_allowed_per_game)

    return defense_stats


def predict_winners(schedule, offense_stats, defense_stats):
    """Predict winner for each matchup, including margin of victory."""
    print 'Picks:'

    keys = schedule.keys()
    keys.sort()
    for key in keys:
        away_team = key
        home_team = schedule[key]

        try:
            away_pts_scored = offense_stats[away_team]
            home_pts_scored = offense_stats[home_team]
        except KeyError, e:
            print 'Error: Key {} not found in dictionary offense_stats'.format(str(e))
            continue

        try:
            away_pts_allowed = defense_stats[away_team]
            home_pts_allowed = defense_stats[home_team]
        except KeyError, e:
            print 'Error: Key {} not found in dictionary defense_stats'.format(str(e))
            continue

        outcome = away_pts_scored - home_pts_scored + home_pts_allowed - away_pts_allowed
        if outcome < 0:
            # If outcome is negative, then home_team is picked
            winner = home_team
            margin = outcome * -1
        else:
            winner = away_team
            margin = outcome

        away = '{} ({:.1f}, {:.1f})'.format(away_team, away_pts_scored, away_pts_allowed)
        home = '{} ({:.1f}, {:.1f})'.format(home_team, home_pts_scored, home_pts_allowed)
        pick = '{} by {:.1f}'.format(winner, margin)

        print '\n{:30}@     {:30}->     {}'.format(away, home, pick)


if __name__ == "__main__":
    main()
