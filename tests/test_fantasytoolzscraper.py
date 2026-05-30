import numpy as np
import pandas as pd
import pytest

from fantasytoolz import fantasytoolzscraper as fts


def test_analyze_team_batting_order_counts_each_lineup_spot(monkeypatch):
    calls = []
    lineup_rows = np.array(
        [
            [
                b"2024-03-28",
                b" Mookie Betts",
                b" Freddie Freeman",
                b" Will Smith",
                b" Max Muncy",
                b" Teoscar Hernandez",
                b" Jason Heyward",
                b" James Outman",
                b" Gavin Lux",
                b" Miguel Rojas",
            ],
            [
                b"2024-03-29",
                b" Mookie Betts",
                b" Shohei Ohtani",
                b" Freddie Freeman",
                b" Will Smith",
                b" Max Muncy",
                b" Teoscar Hernandez",
                b" James Outman",
                b" Gavin Lux",
                b" Miguel Rojas",
            ],
        ],
        dtype="S26",
    )

    def fake_genfromtxt(url, delimiter, dtype, skip_header):
        calls.append((url, delimiter, dtype, skip_header))
        return lineup_rows

    monkeypatch.setattr(fts.np, "genfromtxt", fake_genfromtxt)

    result = fts.analyze_team_batting_order(2024, "LAD")

    assert calls == [
        (
            f"{fts.BATTING_ORDER_BASE_URL}/2024/LAD.csv",
            ",",
            "S26",
            1,
        )
    ]
    np.testing.assert_array_equal(result["Mookie Betts"], [2, 0, 0, 0, 0, 0, 0, 0, 0])
    np.testing.assert_array_equal(
        result["Freddie Freeman"], [0, 1, 1, 0, 0, 0, 0, 0, 0]
    )
    np.testing.assert_array_equal(result["Shohei Ohtani"], [0, 1, 0, 0, 0, 0, 0, 0, 0])


def test_get_all_lineups_reads_season_aggregate(monkeypatch):
    calls = []
    expected = pd.DataFrame({"date": ["2024-03-28"], "team": ["LAD"]})

    def fake_read_csv(url):
        calls.append(url)
        return expected

    monkeypatch.setattr(fts.pd, "read_csv", fake_read_csv)

    result = fts.get_all_lineups("2024")

    pd.testing.assert_frame_equal(result, expected)
    assert calls == [f"{fts.BATTING_ORDER_BASE_URL}/Aggregate/2024-all-lineups.csv"]


def test_get_team_lineup_filters_all_lineups(monkeypatch):
    lineups = pd.DataFrame(
        {
            "date": ["2024-03-28", "2024-03-28", "2024-03-29"],
            "team": ["LAD", "SD", "LAD"],
            "lineup1": ["Mookie Betts", "Xander Bogaerts", "Mookie Betts"],
        }
    )
    monkeypatch.setattr(fts, "get_all_lineups", lambda year: lineups)

    result = fts.get_team_lineup("2024", "LAD")

    assert result["team"].tolist() == ["LAD", "LAD"]
    assert result["date"].tolist() == ["2024-03-28", "2024-03-29"]


def test_get_date_lineups_uses_date_year_and_filters(monkeypatch):
    calls = []
    lineups = pd.DataFrame(
        {
            "date": ["2024-03-28", "2024-03-29"],
            "team": ["LAD", "LAD"],
        }
    )

    def fake_get_all_lineups(year):
        calls.append(year)
        return lineups

    monkeypatch.setattr(fts, "get_all_lineups", fake_get_all_lineups)

    result = fts.get_date_lineups("2024-03-28")

    assert calls == ["2024"]
    assert result["date"].tolist() == ["2024-03-28"]


def test_analyze_all_teams_requires_supported_year():
    with pytest.raises(ValueError, match="2021 or later"):
        fts.analyze_all_teams("2020")


def test_analyze_all_teams_reads_player_summary(monkeypatch):
    calls = []
    expected = pd.DataFrame({"player": ["Mookie Betts"], "bat1": [90]})

    def fake_read_csv(url):
        calls.append(url)
        return expected

    monkeypatch.setattr(fts.pd, "read_csv", fake_read_csv)

    result = fts.analyze_all_teams(2024)

    pd.testing.assert_frame_equal(result, expected)
    assert calls == [
        f"{fts.BATTING_ORDER_BASE_URL}/Aggregate/Summaries/2024player-batting-order.csv"
    ]


def test_get_date_matchups_reads_predictions_and_filters_date(monkeypatch):
    calls = []
    matchups = pd.DataFrame(
        {
            "date": ["2024-03-28", "2024-03-29"],
            "home": ["LAD", "SD"],
            "away": ["STL", "SF"],
        }
    )

    def fake_read_csv(url):
        calls.append(url)
        return matchups

    monkeypatch.setattr(fts.pd, "read_csv", fake_read_csv)

    result = fts.get_date_matchups("2024-03-28")

    assert calls == [f"{fts.PREDICTIONS_BASE_URL}/2024/2024-03-28.csv"]
    assert result["date"].tolist() == ["2024-03-28"]
    assert result["home"].tolist() == ["LAD"]


def test_get_date_matchups_can_read_validation_archive(monkeypatch):
    calls = []
    matchups = pd.DataFrame({"date": ["2024-03-28"], "home": ["LAD"]})

    def fake_read_csv(url):
        calls.append(url)
        return matchups

    monkeypatch.setattr(fts.pd, "read_csv", fake_read_csv)

    fts.get_date_matchups("2024-03-28", postfacto=True)

    assert calls == [f"{fts.PREDICTIONS_BASE_URL}/2024/2024-03-28validation.csv"]
