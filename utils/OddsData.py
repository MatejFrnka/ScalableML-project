import pandas as pd
import os

from consts import *


def get_all_paths():
  basePath = './data/soccer/historical/'
  leagues = os.listdir(basePath)
  paths = []
  for league in leagues:
    files = os.listdir(basePath + str(league) + "/")
    for file in files:
      paths.append(basePath + str(league) + "/" + str(file))

  return paths

def sort_odds_by_date(df):
  df.sort_values('date', inplace=True)
  df = df.reset_index().drop('index', axis=1)
  return df

def read_all_odds(sortedDate=True):
  paths = get_all_paths()
  df_list = [pd.read_csv(path, index_col=[0]) for path in paths]
  df_keep = []
  for d in df_list:
    d.columns =  map(str.lower,d.columns)
    if len(d) > 1000:
      df_keep.append(d)
  df = pd.concat(df_keep)
  if sortedDate:
    df = sort_odds_by_date(df)
  return df

def read_odds(countries='all', leagues='all', sortedDate=True):
  if countries=='all' and leagues=='all':
    return read_all_odds(sortedDate=sortedDate)

  if type(countries) != list:
    countries = [countries]

  if type(leagues) != list:
    leagues = [leagues]

  paths = get_all_paths()
  df_list = []
  for path in paths:
    for country in countries:
      if leagues=='all' and country in path:
        df_list.append(pd.read_csv(path, index_col=[0]))
      else:
        for league in leagues:
          if (country + '/' + league) in path:
            df_list.append(pd.read_csv(path, index_col=[0]))

  df = pd.concat(df_list)
  df.columns= map(str.lower,df.columns)
  if sortedDate:
    df = sort_odds_by_date(df)

  return df




def drop_nan_cols(df):
  pinnNaN = max(df[['ho_pinnacle', 'do_pinnacle', 'ao_pinnacle', 'hc_pinnacle', 'dc_pinnacle', 'ac_pinnacle']].isna().sum())

  for column in df:
    numNaN = df[column].isna().sum()
    if numNaN > pinnNaN:
      df = df.drop(column, axis=1)

  return df

def drop_nan_rows(df):
  df = df.dropna(axis=0)
  df = df.drop_duplicates()
  df = df.reset_index().drop('index', axis=1)
  return df

def drop_duplicates(df):
  df = df.drop_duplicates()
  df = df.reset_index().drop('index', axis=1)
  return df

def remove_nan_vals(df):
  df = drop_nan_cols(df)
  df = drop_nan_rows(df)
  return df





'''
Transform odds into probability (ignoring the "cut" the bookies get)
Loop through all columns, if they start with '(HO,AO,DO,HC,AC,DC) we assume it is a bet from a bookie
'''
def transform_odds_to_probs(df):
  # Loop through all columns, if they start with '(HO,AO,DO,HC,AC,DC) we assume it is a bet from a bookie
  #Then transform it into a probablity (ignoring cut from bookies)
  for i in range(len(df.columns)):
    if df.columns[i].startswith(('ho','ao','do','hc','ac','dc')):
      df.iloc[:,[i]] = df.iloc[:,[i]].apply(lambda j : 1/j)

  return df

def drop_bookies(df, keep=['pinnacle']):
  for col in df:
    drop = True
    if col.startswith(('ho','ao','do','hc','ac','dc')):
      for bookie in keep:
        if bookie in col:
          drop = False
      if drop:
        df = df.drop(col, axis=1)
  return df

def drop_date_time(df):
  return df.drop(['date', 'time'], axis=1)


# Create targets for dataframe
def create_target(row):
    if row[FTHG] > row[FTAG]:
      return 'H'
    elif row[FTAG] > row[FTHG]:
      return 'A'
    else:
      return 'D'

def calculate_targets(df):
  df['target'] = df.apply(lambda row: create_target(row), axis=1)
  return df


if __name__ == "__main__":
  df = read_all_odds()
  print(df)
  df = df.drop_duplicates()
  print(df)