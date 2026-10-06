import pandas as pd
import pytest

import mlbstatscraping as ss
from fangraphs import fangraphsscraper as fgs


class FangraphsResponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return {"data": self._data}


@pytest.fixture
def sample_hitting_data():
    return pd.DataFrame(
        {
            "Name": ["Mookie Betts"],
            "Team": ["LAD"],
            "Season": [2024],
            "G": [116],
            "PA": [516],
            "HR": [19],
        }
    )


@pytest.fixture
def sample_pitching_data():
    return pd.DataFrame(
        {
            "Name": ["Tarik Skubal"],
            "Team": ["DET"],
            "season": [2024],
            "G": [31],
            "IP": [192.0],
            "SO": [228],
        }
    )


def test_get_fangraphs_data_hitting_calls_hitting_scraper(
    monkeypatch, sample_hitting_data
):
    calls = []

    def fake_hitting_scraper(years, daystart="", dayend="", advanced=False):
        calls.append((years, daystart, dayend, advanced))
        return sample_hitting_data

    monkeypatch.setattr(ss.fgs, "grab_fangraphs_hitting_data", fake_hitting_scraper)

    result = ss.get_fangraphs_data(
        "hitting",
        ["2024"],
        daystart="2024-04-01",
        dayend="2024-05-01",
        advanced=True,
    )

    pd.testing.assert_frame_equal(result, sample_hitting_data)
    assert calls == [(["2024"], "2024-04-01", "2024-05-01", True)]


def test_get_fangraphs_data_pitching_calls_pitching_scraper(
    monkeypatch, sample_pitching_data
):
    calls = []

    def fake_pitching_scraper(years, daystart="", dayend="", advanced=False):
        calls.append((years, daystart, dayend, advanced))
        return sample_pitching_data

    monkeypatch.setattr(ss.fgs, "grab_fangraphs_pitching_data", fake_pitching_scraper)

    result = ss.get_fangraphs_data("pitching", ["2024"])

    pd.testing.assert_frame_equal(result, sample_pitching_data)
    assert calls == [(["2024"], "", "", False)]


def test_invalid_stat_type_raises_error(monkeypatch):
    def scraper_should_not_be_called(*args, **kwargs):
        raise AssertionError("Fangraphs scraper should not be called")

    monkeypatch.setattr(
        ss.fgs, "grab_fangraphs_hitting_data", scraper_should_not_be_called
    )
    monkeypatch.setattr(
        ss.fgs, "grab_fangraphs_pitching_data", scraper_should_not_be_called
    )

    with pytest.raises(ValueError, match="Invalid playertype"):
        ss.get_fangraphs_data("invalid_type", ["2024"])


def test_daystart_year_must_match_requested_years(monkeypatch):
    def scraper_should_not_be_called(*args, **kwargs):
        raise AssertionError("Fangraphs scraper should not be called")

    monkeypatch.setattr(
        ss.fgs, "grab_fangraphs_hitting_data", scraper_should_not_be_called
    )

    with pytest.raises(ValueError, match=r"daystart year \(2023\)"):
        ss.get_fangraphs_data("hitting", ["2024"], daystart="2023-04-01")


def test_daystart_year_can_match_any_requested_year(monkeypatch, sample_hitting_data):
    calls = []

    def fake_hitting_scraper(years, daystart="", dayend="", advanced=False):
        calls.append((years, daystart, dayend, advanced))
        return sample_hitting_data

    monkeypatch.setattr(ss.fgs, "grab_fangraphs_hitting_data", fake_hitting_scraper)

    result = ss.get_fangraphs_data(
        "hitting", ["2023", "2024"], daystart="2023-04-01"
    )

    pd.testing.assert_frame_equal(result, sample_hitting_data)
    assert calls == [(["2023", "2024"], "2023-04-01", "", False)]


def test_hitting_scraper_uses_full_season_dates_by_default(monkeypatch):
    requests = []

    def fake_get(url, params, headers=None):
        requests.append((url, params, headers))
        return FangraphsResponse(
            [
                {
                    "Name": "Mookie Betts",
                    "Team": "LAD",
                    "Season": "2024",
                    "G": "116",
                    "PA": "516",
                    "wRC+": "145",
                }
            ]
        )

    monkeypatch.setattr(fgs.requests, "get", fake_get)

    result = fgs.grab_fangraphs_hitting_data(["2024"])

    assert len(result) == 1
    assert "wRC+" not in result.columns
    assert requests[0][1]["startdate"] == "2024-01-01"
    assert requests[0][1]["enddate"] == "2024-12-31"
    assert "User-Agent" in requests[0][2]


def test_hitting_scraper_maps_daystart_and_dayend_to_fangraphs_dates(monkeypatch):
    requests = []

    def fake_get(url, params, headers=None):
        requests.append((url, params, headers))
        return FangraphsResponse(
            [
                {
                    "Name": "Mookie Betts",
                    "Team": "LAD",
                    "Season": "2024",
                    "G": "116",
                    "PA": "516",
                    "wRC+": "145",
                }
            ]
        )

    monkeypatch.setattr(fgs.requests, "get", fake_get)

    result = fgs.grab_fangraphs_hitting_data(
        ["2024"], daystart="2024-04-01", dayend="2024-05-01"
    )

    assert len(result) == 1
    assert requests[0][1]["startdate"] == "2024-04-01"
    assert requests[0][1]["enddate"] == "2024-05-01"


def test_hitting_scraper_advanced_mode_returns_all_columns(monkeypatch):
    def fake_get(url, params, headers=None):
        return FangraphsResponse(
            [
                {
                    "Name": "Mookie Betts",
                    "Team": "LAD",
                    "Season": "2024",
                    "G": "116",
                    "PA": "516",
                    "wRC+": "145",
                }
            ]
        )

    monkeypatch.setattr(fgs.requests, "get", fake_get)

    result = fgs.grab_fangraphs_hitting_data(["2024"], advanced=True)

    assert "wRC+" in result.columns
    assert result.loc[0, "wRC+"] == 145


def test_pitching_scraper_maps_daystart_and_dayend_to_fangraphs_dates(monkeypatch):
    requests = []

    def fake_get(url, params, headers=None):
        requests.append((url, params, headers))
        return FangraphsResponse(
            [
                {
                    "season": "2024",
                    "Name": "Tarik Skubal",
                    "Team": "DET",
                    "G": "31",
                    "IP": "192.0",
                    "K/9": "10.69",
                }
            ]
        )

    monkeypatch.setattr(fgs.requests, "get", fake_get)

    result = fgs.grab_fangraphs_pitching_data(
        ["2024"], daystart="2024-04-01", dayend="2024-05-01"
    )

    assert len(result) == 1
    assert requests[0][1]["startdate"] == "2024-04-01"
    assert requests[0][1]["enddate"] == "2024-05-01"


def test_pitching_scraper_advanced_mode_returns_all_columns(monkeypatch):
    def fake_get(url, params, headers=None):
        return FangraphsResponse(
            [
                {
                    "season": "2024",
                    "Name": "Tarik Skubal",
                    "Team": "DET",
                    "G": "31",
                    "IP": "192.0",
                    "K/9": "10.69",
                }
            ]
        )

    monkeypatch.setattr(fgs.requests, "get", fake_get)

    result = fgs.grab_fangraphs_pitching_data(["2024"], advanced=True)

    assert "K/9" in result.columns
    assert result.loc[0, "K/9"] == 10.69


def test_pitching_scraper_advanced_mode_preserves_throws(monkeypatch):
    def fake_get(url, params, headers=None):
        return FangraphsResponse(
            [
                {
                    "season": "2024",
                    "Name": "Tarik Skubal",
                    "Team": "DET",
                    "Throws": "L",
                    "G": "31",
                    "IP": "192.0",
                    "K/9": "10.69",
                }
            ]
        )

    monkeypatch.setattr(fgs.requests, "get", fake_get)

    result = fgs.grab_fangraphs_pitching_data(["2024"], advanced=True)

    assert result.loc[0, "Throws"] == "L"
    assert result.loc[0, "K/9"] == 10.69
