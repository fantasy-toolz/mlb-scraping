


import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import numpy as np

def _strip_html(value):
    """Return cell text with any embedded HTML tags removed."""
    if pd.isna(value):
        return value
    return BeautifulSoup(str(value), "html.parser").get_text(strip=True)


def _clean_name_team_columns(df):
    for col in ['Name', 'Team']:
        if col in df.columns:
            df[col] = df[col].map(_strip_html)
    return df


FANGRAPHS_TEXT_COLUMNS = {
    'Name',
    'Team',
    'PlayerName',
    'PlayerNameRoute',
    'TeamName',
    'TeamNameAbb',
    'Pos',
    'position',
    'positionDB',
    'Bats',
    'Throws',
}


def _coerce_numeric_columns(df):
    for col in df.columns:
        if col not in FANGRAPHS_TEXT_COLUMNS:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def _fangraphs_date_range(year, daystart='', dayend=''):
    return daystart or f"{year}-01-01", dayend or f"{year}-12-31"


def grab_fangraphs_hitting_data(years,daystart='',dayend='',verbose=False,advanced=False):
    """get fangraphs hitting data for a given year"""

    year_dfs = []

    for year in years:
        url = "https://www.fangraphs.com/api/leaders/major-league/data"
        startdate, enddate = _fangraphs_date_range(year, daystart, dayend)

        params = {
            "pos": "all",
            "stats": "bat",
            "lg": "all",
            "qual": "0",
            "type": "0",
            "season": str(year),
            "season1": str(year),
            "month": "1000",
            "ind": "0",
            "team": "0",
            "rost": "0",
            "age": "0",
            "filter": "",
            "players": "0",
            "startdate": startdate,
            "enddate": enddate,

            # sorting
            "sortstat": "PA",      # or whatever column index 3 maps to
            "sortdir": "default",

            # pagination
            "pageitems": "10000",
            "pagenum": "1",

            # often present
            "postseason": ""
        }

        r = requests.get(url, params=params)
        r.raise_for_status()

        data = r.json()["data"]

        # make a subset selection
        columns = [
            'Name',
            'Team',
            'Season',
            'Age',
            'G',
            'AB',
            'PA',
            'H',
            '1B',
            '2B',
            '3B',
            'HR',
            'R',
            'RBI',
            'BB',
            'IBB',
            'SO',
            'HBP',
            'SF',
            'SH',
            'GDP',
            'SB',
            'CS',
            'AVG',
            'GB',
            'FB',
            'LD',
        ]

        if advanced:
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame(data, columns=columns)
        # Great, our Data is in a list of lists: much more pythonic. Let's birth a pandas table!
        #df = pd.DataFrame(rows, columns=headers)
        df = _clean_name_team_columns(df)

        # Convert stat columns to numeric while preserving identity columns.
        df = _coerce_numeric_columns(df)

        # trim anyone who didn't actually play
        df = df.loc[df['G'].astype(float) > 0]

        df['Year'] = year

        year_dfs.append(df)

    df = year_dfs[0]
    for year in year_dfs[1:]:
        df = pd.concat([df, year])
    return df


def grab_fangraphs_pitching_data(years,daystart='',dayend='',verbose=False,advanced=False):
    """get fangraphs pitching data for a given year"""

    year_dfs = []

    for year in years:
        url = "https://www.fangraphs.com/api/leaders/major-league/data"
        startdate, enddate = _fangraphs_date_range(year, daystart, dayend)

        params = {
            "pos": "all",
            "stats": "pit",
            "lg": "all",
            "qual": "0",
            "type": "0",
            "season": str(year),
            "season1": str(year),
            "month": "1000",
            "ind": "0",
            "team": "0",
            "rost": "0",
            "age": "0",
            "filter": "",
            "players": "0",
            "startdate": startdate,
            "enddate": enddate,

            # sorting
            "sortstat": "IP",      # or whatever column index 3 maps to
            "sortdir": "default",

            # pagination
            "pageitems": "10000",
            "pagenum": "1",

            # often present
            "postseason": ""
        }

        r = requests.get(url, params=params)
        r.raise_for_status()

        data = r.json()["data"]

        # make a subset selection
        columns = [
            'season',
            'Name',
            'Team',
            'Age',
            'W',
            'L',
            'ERA',
            'G',
            'GS',
            'QS',
            'CG',
            'ShO',
            'SV',
            'HLD',
            'BS',
            'IP',
            'TBF',
            'H',
            'R',
            'ER',
            'HR',
            'BB',
            'IBB',
            'HBP',
            'WP',
            'BK',
            'SO',
        ]

        if advanced:
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame(data, columns=columns)
        # Great, our Data is in a list of lists: much more pythonic. Let's birth a pandas table!
        #df = pd.DataFrame(rows, columns=headers)
        df = _clean_name_team_columns(df)

        # Convert stat columns to numeric while preserving identity columns.
        df = _coerce_numeric_columns(df)

        # trim anyone who didn't actually play
        df = df.loc[df['G'].astype(float) > 0]

        df['Year'] = year

        year_dfs.append(df)

    df = year_dfs[0]
    for year in year_dfs[1:]:
        df = pd.concat([df, year])
    return df
