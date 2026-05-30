# mlb-scraping
## FantasyToolz
## v2.1

Scraping capabilities for several major MLB and Fantasy MLB sources, consolidated under one interface.

### Installation

After obtaining the repository from GitHub,
```bash
git clone git@github.com:fantasy-toolz/stat-scraping.git
```
install with 
```bash
pip install .
```

### Batting Orders
To scrape batting order statistics for a team,

```python
import mlbstatscraping as mss

year = '2024'
team = 'ATL'

ATL = mss.get_fantasytoolz_lineups(team,year)
AllPlayers = mss.get_fantasytoolz_lineup_summary(year)

date = '2024-08-31'
DateLineups = mss.get_fantasytoolz_date_lineups(date)

TeamLineups = mss.get_fantasytoolz_team_lineup(year,team)

AllLineups = mss.get_fantasytoolz_all_lineups(year)
```

### MLB Predictions

Get daily Fantasy Toolz predictions for matchups:

```python
import mlbstatscraping as mss

date = '2024-08-31'
Matchups = mss.get_fantasytoolz_date_matchups(date)
```

Cross-matching with the matchups:
```python 
import mlbstatscraping as mss
import pandas as pd

date = '2024-06-25'
Matchups = mss.get_fantasytoolz_date_matchups(date)
DateLineups = mss.get_fantasytoolz_date_lineups(date)

HomeLineups = pd.merge(Matchups,DateLineups,left_on="hometeam",right_on="team")
AwayLineups = pd.merge(Matchups,DateLineups,left_on="awayteam",right_on="team")

```


## Fangraphs

Get stats from Fangraphs:

```python
import mlbstatscraping as mss

HittingDF = mss.get_fangraphs_data('hitting',['2024'])
PitchingDF = mss.get_fangraphs_data('pitching',['2024'])
```

Specific date ranges can also be scraped in a season, e.g. by
```python
HittingDF = ss.get_fangraphs_data('hitting',['2024'],'2024-04-01','2024-05-01')
```

## FantasyPros

Get projections from FantasyPros:

```python
import mlbstatscraping as mss
HittingDF = mss.get_fantasypros_projections('hitters',preseason=True)
```

Get the consensus draft order:
```python
DraftOrder = mss.get_fantasy_pros_rank()
```