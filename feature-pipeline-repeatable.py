from datetime import datetime

import hopsworks
import pandas as pd
from consts import *
from utils.Features import calculate_features
from utils.Hopsworks import get_football_featureview

KNOWN_COLUMNS = [FTHG, FTAG, HomeTeam, AwayTeam, AwayCloseOdds, HomeCloseOdds, DrawCloseOdds, AwayOpenOdds,
                 HomeOpenOdds, DrawOpenOdds, 'league', 'country', 'date']


def new_data_placeholder():
    df = pd.DataFrame(
        columns=KNOWN_COLUMNS,
        data=[
            [1, 5, 'Burton', 'Plymouth', 0.3, 0.3, 0.4, 0.29, 0.31, 0.4, 'league-one', 'england', datetime.now()],
            [1, 1, 'AlemanniaAachen', 'PreussenMunster', 0.3, 0.3, 0.4, 0.29, 0.31, 0.4, '3-liga', 'germany',
             datetime.now()],
        ]
    )
    return df


# You have to set the environment variable 'HOPSWORKS_API_KEY' for login to succeed
project = hopsworks.login()
# fs is a reference to the Hopsworks Feature Store
fs = project.get_feature_store()

feature_view = get_football_featureview(fs)

old_data, _ = feature_view.training_data()
old_data['date'] = pd.to_datetime(old_data['date'])
old_data = old_data.sort_values(by='date', ascending=True)

new_data = new_data_placeholder()
new_cnt = len(new_data)

data = pd.concat([old_data[KNOWN_COLUMNS], new_data])
data = calculate_features(data)

fg_football = fs.get_feature_group(name="fg_football", version=FG_VERSION)
fg_football.insert(data.tail(new_cnt))
