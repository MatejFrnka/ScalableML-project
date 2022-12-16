import math
import urllib

import pandas as pd

FOOTBALL_DATA_URL = "https://www.football-data.co.uk/mmz4281/"  # 2223/E0.csv
FOOTBALL_DATA_YEARS = [*range(93, 100), *range(0, 23)]
# FOOTBALL_DATA_YEARS = [*range(0, 23)]
FOOTBALL_DATA_LEAGUES = ["EC", "E3", "E2", "E1", "E0"]


def from_football_data():
    def normalize_date(str_val):
        if type(str_val) != str and math.isnan(str_val):
            return None
        vals = str_val.split("/")
        assert len(vals) == 3
        year = vals[-1]
        if len(year) == 2:
            if int(year) < 70:
                year = "20" + year
            else:
                year = "19" + year
        return f"{vals[0]}/{vals[1]}/{year}"

    result = pd.DataFrame()
    for year in FOOTBALL_DATA_YEARS:
        for league in FOOTBALL_DATA_LEAGUES:
            url = FOOTBALL_DATA_URL + f"{str(year).zfill(2)}{str((year + 1) % 100).zfill(2)}/{league}.csv"
            try:
                t = pd.read_csv(url, index_col=False, header=0, on_bad_lines="warn", encoding_errors="replace")
            except urllib.error.HTTPError:
                print(f"Not found: {url}")
                continue
            except Exception as e:
                print(f"Unknown error: {url}")
                print(e)
                continue
            t["Date"] = t["Date"].apply(normalize_date)
            t["Date"] = pd.to_datetime(t["Date"], format="%d/%m/%Y")
            t["Season"] = f"{str(year).zfill(2)}{str((year + 1) % 100).zfill(2)}"
            result = pd.concat([t, result])
            print(f"Downloaded: {url}")

    result = result.dropna(axis=1, how='all')
    result = result.dropna(axis=0, how='all')
    result = result.reset_index()
    return result


if __name__ == "__main__":
    res = from_football_data()
    res.to_csv("data/football_data.csv")
