import hopsworks

from utils.Hopsworks import get_football_featuregroup
from utils.OddsData import *
from utils.Features import *
from consts import *
import pandas as pd

data_df = read_odds(countries='all')
data_df = remove_nan_vals(data_df)
data_df["date"] = pd.to_datetime(data_df["date"])
data_df = transform_odds_to_probs(data_df)
data_df = drop_duplicates(data_df)

# hopsworks doesn't support capital letters in columns
# convert everything to lowercase
data_df.columns = map(str.lower, data_df.columns)
data_df = data_df.sort_values(by='date', ascending=True)
data_df = calculate_features(data_df)


data_df = data_df[ALL_COLUMNS].copy()

project = hopsworks.login()
fs = project.get_feature_store()
fg_football = get_football_featuregroup(fs)

fg_football.insert(data_df)
