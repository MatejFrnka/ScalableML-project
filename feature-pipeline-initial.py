import hopsworks
from utils.OddsData import *
from utils.Features import *
from consts import *
import pandas as pd

data_df = read_odds(countries='all')
data_df = remove_nan_vals(data_df)
data_df["Date"] = pd.to_datetime(data_df["Date"])
data_df = transform_odds_to_probs(data_df)
data_df = drop_duplicates(data_df)

# hopsworks doesn't support capital letters in columns
# convert everything to lowercase
data_df.columns = map(str.lower, data_df.columns)
data_df = data_df.sort_values(by='date', ascending=True)
data_df = calculate_features(data_df)

# todo calculate games in last x days

data_df = data_df[ALL_COLUMNS].copy()

project = hopsworks.login()
fs = project.get_feature_store()
fg_football = fs.get_or_create_feature_group(
    name="fg_football",
    version=FG_VERSION,
    primary_key=KEY_COLUMNS,
    event_time=['date'],
    description="Football data")

fg_football.insert(data_df)
