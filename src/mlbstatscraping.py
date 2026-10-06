

from fantasypros import fantasyprosscraper as fps
from fantasytoolz import fantasytoolzscraper as fts



def get_fantasypros_projections(playertype,preseason=False):
    return fps.get_fantasy_pros_proj(playertype,preseason)


def get_fantasypros_ranks():
    return fps.get_fantasy_pros_rank()

"""
Fantasy Toolz block
"""

def get_fantasytoolz_lineups(team,year=2024):
    if int(year)<2021:
        raise ValueError('Year must be 2021 or later.') 
    return fts.analyze_team_batting_order(year,team)


def get_fantasytoolz_lineup_summary(year):
    if int(year)<2021:
        raise ValueError('Year must be 2021 or later.') 
    return fts.analyze_all_teams(year)


def get_fantasytoolz_date_lineups(date):
    return fts.get_date_lineups(date)

def get_fantasytoolz_team_lineup(year,team):
    return fts.get_team_lineup(year,team)

def get_fantasytoolz_all_lineups(year):
    return fts.get_all_lineups(year)

def get_fantasytoolz_date_matchups(date):
    return fts.get_date_matchups(date)
