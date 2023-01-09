import hopsworks

from utils.Hopsworks import get_football_featuregroup
from utils.OddsData import *
from utils.Features import *
from consts import *
import pandas as pd

project = hopsworks.login()
fs = project.get_feature_store()
fg_football = get_football_featuregroup(fs)

data_df = read_odds(countries='all')
data_df = drop_bookies(data_df)
data_df["date"] = pd.to_datetime(data_df["date"])
data_df = transform_odds_to_probs(data_df)
data_df = drop_duplicates(data_df)

# hopsworks doesn't support capital letters in columns
# convert everything to lowercase
data_df.columns = map(str.lower, data_df.columns)
data_df = data_df.sort_values(by='date', ascending=True)
print('Adding targets: h_win, d_win, a_win')
data_df = add_targets_feature(data_df)

print('Adding Last FTR')
data_df = calculate_last_ftr_feature(data_df)

print('Adding MMR')
data_df = calculate_mmr_feature(data_df)

print('Adding Points')
data_df = calculate_points_feature(data_df, num_matches=5)
data_df = calculate_points_feature(data_df, num_matches=10)
data_df = calculate_points_feature(data_df, num_matches=15)

print('Adding Winstreak')
data_df = calculate_win_streak_feature(data_df)

# remove nan values
data_df = remove_nan_vals(data_df)

print('Adding Last Close')
data_df = calculate_last_close_feature(data_df)

print('Adding Realized EV')
data_df = calculate_realized_ev_feature(data_df, num_matches=3)
data_df = calculate_realized_ev_feature(data_df, num_matches=5)
data_df = calculate_realized_ev_feature(data_df, num_matches=9)

print('Adding Shock')
data_df = calculate_shock_feature(data_df, num_matches=1)
data_df = calculate_shock_feature(data_df, num_matches=3)
data_df = calculate_shock_feature(data_df, num_matches=5)


data_df = data_df[ALL_COLUMNS].copy()
fg_football.insert(data_df)
