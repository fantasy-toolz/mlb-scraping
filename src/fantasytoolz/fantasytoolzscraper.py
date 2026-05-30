
"""Helpers for Fantasy Toolz lineup and matchup data.

The functions in this module read public CSV files maintained by Fantasy Toolz
on GitHub.  Batting-order files contain one row per team game with the date in
the first column and lineup spots one through nine in the remaining columns.
Aggregate files are returned as pandas data frames so callers can continue to
filter or join them with other baseball data.
"""

import numpy as np
import pandas as pd


BATTING_ORDER_BASE_URL = (
    "https://raw.githubusercontent.com/fantasy-toolz/batting-order/"
    "refs/heads/main/data"
)
PREDICTIONS_BASE_URL = (
    "https://raw.githubusercontent.com/fantasy-toolz/mlb-predictions/"
    "refs/heads/main/predictions/archive"
)
MIN_LINEUP_YEAR = 2021
LINEUP_SPOTS = 9


def _validate_lineup_year(year):
    """Raise a ValueError when a lineup summary year is not available."""
    if int(year) < MIN_LINEUP_YEAR:
        raise ValueError("Year must be 2021 or later.")


def _year_from_date(date):
    """Return the year portion from a YYYY-MM-DD date string."""
    return date.split("-")[0]


def analyze_team_batting_order(year, team):
    """Count how often each player appeared in each batting-order spot.

    Parameters
    ----------
    year : int or str
        MLB season to fetch from the Fantasy Toolz batting-order repository.
    team : str
        Team abbreviation used by the source CSV, such as ``"LAD"``.

    Returns
    -------
    dict[str, numpy.ndarray]
        Mapping of player name to a nine-element array.  Each array position
        contains the number of games the player batted in that lineup spot.
        For example, index ``0`` counts leadoff appearances and index ``8``
        counts ninth-place appearances.
    """
    position_total = {}
    url = f"{BATTING_ORDER_BASE_URL}/{year}/{team}.csv"
    lineup_rows = np.genfromtxt(url, delimiter=",", dtype="S26", skip_header=1)
    lineup_rows = np.atleast_2d(lineup_rows)

    print("team: ", team, " games played: ", len(lineup_rows[:, 0]))

    for row in lineup_rows:
        for lineup_spot, player in enumerate(row[1 : LINEUP_SPOTS + 1]):
            player_name = player.decode().lstrip()
            if player_name not in position_total:
                position_total[player_name] = np.zeros(LINEUP_SPOTS)
            position_total[player_name][lineup_spot] += 1

    return position_total


def get_all_lineups(year):
    """Return every recorded batting lineup for a season.

    Parameters
    ----------
    year : int or str
        MLB season available in the Fantasy Toolz aggregate lineup data.

    Returns
    -------
    pandas.DataFrame
        Data frame containing all teams and dates from the season aggregate
        lineup file.
    """
    url = f"{BATTING_ORDER_BASE_URL}/Aggregate/{year}-all-lineups.csv"
    return pd.read_csv(url)


def get_team_lineup(year, team):
    """Return all recorded lineups for one team in a season."""
    all_lineups = get_all_lineups(year)
    return all_lineups[all_lineups["team"] == team]


def get_date_lineups(date):
    """Return all recorded lineups for a single date.

    The date must use ``YYYY-MM-DD`` format; its year selects the aggregate
    season file before filtering to the requested date.
    """
    year = _year_from_date(date)
    all_lineups = get_all_lineups(year)
    return all_lineups[all_lineups["date"] == date]


def analyze_all_teams(year):
    """Return the season batting-order summary for every player.

    Parameters
    ----------
    year : int or str
        MLB season.  Fantasy Toolz aggregate summaries are available for 2021
        and later.

    Returns
    -------
    pandas.DataFrame
        Aggregate player batting-order summary from Fantasy Toolz.
    """
    _validate_lineup_year(year)
    url = f"{BATTING_ORDER_BASE_URL}/Aggregate/Summaries/{year}player-batting-order.csv"
    return pd.read_csv(url)


def get_date_matchups(date, postfacto=False):
    """Return predicted or validated matchups for a single date.

    Parameters
    ----------
    date : str
        Date to fetch in ``YYYY-MM-DD`` format.
    postfacto : bool, default False
        When ``False``, read the prediction archive.  When ``True``, read the
        validation archive for the same date.

    Returns
    -------
    pandas.DataFrame
        Matchup rows whose ``date`` column equals the requested date.
    """
    year = _year_from_date(date)
    suffix = "validation" if postfacto else ""
    url = f"{PREDICTIONS_BASE_URL}/{year}/{date}{suffix}.csv"
    all_matchups = pd.read_csv(url)
    return all_matchups[all_matchups["date"] == date]
