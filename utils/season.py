import datetime

SEASON_NAME_MAP = {
    "2014": "2014/15",
    "2015": "2015/16",
    "2016": "2016/17",
    "2017": "2017/18",
    "2018": "2018/19",
    "2019": "2019/20",
    "2020": "2020/21",
    "2021": "2021/22",
    "2022": "2022/23",
    "2023": "2023/24",
    "2024": "2024/25",
    "2025": "2025/26",
}

def get_current_understat_season(dt=None):
    """
    Returns the Understat season start year.
    Example: 2025 for 2025/26 season.
    """
    if dt is None:
        dt = datetime.datetime.now()

    return dt.year if dt.month >= 7 else dt.year - 1

# --- helper: convert season year to "YYYY/YY" string ---
def season_to_name(season_year: int | str):
    """
    Takes 2025 → returns '2025/26'
    """
    season_year = str(season_year)
    return SEASON_NAME_MAP.get(season_year, season_year)