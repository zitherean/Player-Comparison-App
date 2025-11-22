import asyncio
import aiohttp
import pandas as pd
from understat import Understat
from utils.partitioned_parquet import write_partitioned_players
import datetime

# Max number of concurrent requests (both semaphore and TCP connector use this) 
# Be friendly to Understat's servers
CONCURRENCY = 6

LEAGUES = ["EPL", "La_liga", "Bundesliga", "Serie_A", "Ligue_1"] # top 5 leagues according to Understat API

# helper to get current season
def get_current_understat_season(dt=None):
    """
    Returns the Understat season start year.
    Example: 2025 for 2025/26 season.
    """
    if dt is None:
        dt = datetime.datetime.now()

    return dt.year if dt.month >= 7 else dt.year - 1

current_season = get_current_understat_season()
SEASONS = list(range(2014, current_season + 1))  # 2014 = 2014/15 ... up to 2025/26 update for next season

# Columns expected to be numeric in raw player totals
NUMBER_COLS = ["games", "time", "goals", "xG", "shots", "assists", 
               "xA", "key_passes", "npg", "npxG", "xGChain", "xGBuildup", "red_cards", "yellow_cards"]

PER_90_COLS = ["goals", "xG", "shots", "assists", "xA", 
               "key_passes", "npg", "npxG", "xGChain", "xGBuildup"]

# ---------------------------HELPER FUNCTIONS---------------------------

# helper to convert columns to numeric
def _to_num(df, cols):
    """Coerce selected columns to numeric (invalid values become NaN)."""
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

# helper to convert to per 90 stats
def _to_per90(df, cols):
    """
    Add <col>_per90 columns by dividing each metric by (time/90).
    - Avoid division by zero by replacing 0 minutes with NA.
    - If 'time' is missing, return df unchanged.
    """
    if "time" not in df.columns:
        return df
    denominator = (df["time"] / 90).replace(0, pd.NA)
    for c in cols:
        if c in df.columns and "time" in df.columns:
            df[c + "_per90"] = df[c] / denominator
    return df

# helper to check base types in dataframe
def _base_types(df):
    """
    Ensure base identifier columns exist with sensible dtypes.
    This prevents dtype surprises when concatenating across seasons/leagues.
    """
    base_cols = {"id": str, "player_name": str, "team_title": str, 
                 "position": str, "league": str, "season": str}
    
    for c, t in base_cols.items():
        if c not in df.columns:
            df[c] = pd.Series(dtype=t)

# add league and season columns to player records
def to_dataframe(league, season, records):
    """
    Convert raw Understat records to a clean DataFrame:
    - attach league/season
    - coerce base dtypes
    - coerce numeric totals
    - compute per-90 features
    """
    for record in records:
        record["league"] = league
        record["season"] = str(season)

    df = pd.DataFrame.from_records(records)

    _base_types(df)

    df["id"] = df["id"].astype(str, errors="ignore")
    df["league"] = df["league"].astype(str)
    df["season"] = df["season"].astype(str)

    df = _to_num(df, NUMBER_COLS)
    df = _to_per90(df, PER_90_COLS)

    return df

# ---------------------------DATA FETCHING FUNCTIONS---------------------------
async def fetch_one(understat: Understat, league: str, season: int):
    """
    Fetch a single league-season from the Understat API.
    Returns a tuple (league, season, records) for downstream processing.
    """
    records = await understat.get_league_players(league, season)
    return league, season, records

async def fetch_one_limited(understat: Understat, sem: asyncio.Semaphore, league: str, season: int):
    """
    Wrapper that respects the concurrency semaphore to avoid overwhelming the API.
    """
    async with sem:
        return await fetch_one(understat, league, season)

async def fetch_all(leagues, seasons):
    """
    Kick off all league-season fetches concurrently.
    - Uses a shared aiohttp.ClientSession and TCPConnector with a limit.
    - Collects successes and exceptions separately for clearer reporting.
    """
    sem = asyncio.Semaphore(CONCURRENCY)
    connector = aiohttp.TCPConnector(limit=CONCURRENCY)
    async with aiohttp.ClientSession(connector=connector) as session:
        us = Understat(session)
        tasks = [fetch_one_limited(us, sem, league, season)
                 for league in leagues
                 for season in seasons]
        # Gather results without failing fast; keep exceptions in the list
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # Split successes from errors for downstream handling
    ok = []
    errors = []
    for result in results:
        if isinstance(result, Exception):
            errors.append(result)
        else:
            ok.append(result)
    return ok, errors

# ---------------------------MAIN---------------------------
async def main():
    """
    Orchestrates fetching, transformation, and partitioned Parquet writes.
    - Logs any fetch errors.
    - Skips empty datasets.
    - Writes each (league, season) partition, here using overwrite to keep only latest pull.
    """
    successes, errors = await fetch_all(LEAGUES, SEASONS)

    # Report any failures (network issues, API errors, etc.)
    for e in errors:
        print(f"Fetch failed {e}")

    for league, season, records in successes:
        df = to_dataframe(league, season, records)
        if df.empty:
            print(f"[INFO] No data for {league} {season}")
            continue
        write_partitioned_players(df, mode="overwrite")


if __name__ == "__main__":
    asyncio.run(main())