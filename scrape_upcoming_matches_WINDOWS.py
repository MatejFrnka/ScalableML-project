from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import numpy as np
from pathlib import Path
import pandas as pd
import time
import re
from utils.OddsData import *
from utils.Features import *

def login(driver):
  login_url = 'https://www.oddsportal.com/login/'

  wait = WebDriverWait(driver, 30)
  driver.get(login_url)

  wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='login-username1']"))).send_keys("Derik1337")
  wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='login-password1']"))).send_keys("D4Cit.W9iC3K4iK")
  wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()

  print('-----Logged in!-----')

  return driver

def extract_open_close_odds(driver, data):
  if len(data.text) <= 4:
    close = float(data.text)
  else:
    close = float(data.text.split('\n')[0])
  
  try:
    ActionChains(driver).move_to_element(data).perform()
    if len(data.text) > 4:
      time.sleep(0.5)
    odds_data = data.find_element_by_xpath("//*[@id='tooltiptext']")
    odds_data = odds_data.get_attribute("innerHTML").split('Opening odds:')[1].replace('<strong>Click to BET NOW</strong>', '').replace('<br>', '')
    open_date = odds_data[0:13]
    if 'Dec' in open_date and datetime.today().month == 1:
      open_date = datetime.strptime(open_date + ', ' + str(datetime.today().year - 1), '%d %b, %H:%M, %Y')
    else:
      open_date = datetime.strptime(open_date + ', ' + str(datetime.today().year), '%d %b, %H:%M, %Y')
    odds = odds_data[13:]
    open = float(re.search('<strong>(.*)</strong>', odds).group(1))
  except:
    print('No Open odds found (ERROR line ~45)!')
    open = close
  
  return open, close, open_date

def strip_day(date_str):
  return date_str.replace('Monday, ', '').replace('Tuesday, ', '').replace('Wednesday, ', '').replace('Thursday, ', '').replace('Friday, ', '').replace('Saturday, ', '').replace('Sunday, ', '').replace('Yesterday, ', '').replace('Today, ', '').replace('Tomorrow, ', '')

def get_meta_data(driver, country, league):
  time.sleep(1)
  teams = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id =" + '"col-content"' + "]/h1"))).text.split(' - ')
  H_team, A_team = teams[0].replace(' ',''), teams[1].replace(' ','')
  
  time.sleep(1)
  date_str = strip_day(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id =" + '"col-content"' + "]/p"))).text)
  date = datetime.strptime(date_str, '%d %b %Y, %H:%M')

  dict = {'Country' : [country], 'League' : [league] ,'H_team' : [H_team], 
          'A_team' : [A_team], 'Date' : [date.date()], 'Time' : [date.time()]}

  return dict

def complete_dict(driver, dict, bookie, home, draw, away):
  b = bookie
  H_open, H_close, Open_time = extract_open_close_odds(driver, home)
  D_open, D_close, Open_time = extract_open_close_odds(driver, draw)
  A_open, A_close, Open_time = extract_open_close_odds(driver, away)

  #'OT_' + b : [Open_time], 
  new_dict = {'HO_' + b : [H_open], 'DO_' + b : [D_open], 'AO_' + b: [A_open],
              'HC_' + b : [H_close], 'DC_' + b : [D_close], 'AC_' + b: [A_close]}

  dict.update(new_dict)
  return dict

def scrape_match_page(driver, country, league):

  dict = get_meta_data(driver, country, league)

  odds_data_table = driver.find_elements_by_xpath("//*[@id =" + '"odds-data-table"' + "]/div[1]/table/tbody/tr")
  num_rows = len(odds_data_table)

  print('Reading odds for ' + str(dict['H_team'][0]) + ' - ' + str(dict['A_team'][0]) + '...')

  for index in (range(1, num_rows)):
    row_data = driver.find_elements_by_xpath("//*[@id =" + '"odds-data-table"' + "]/div[1]/table/tbody/tr[" + str(index) +"]/td")
    bookie, home, draw, away = row_data[0].text.replace(' ', ''), row_data[1], row_data[2], row_data[3]
    if 'Pinnacle' not in bookie:
      continue
    dict = complete_dict(driver, dict, bookie, home, draw, away)
    
  df = pd.DataFrame(dict)
  return df

def scrape_matches(driver, match_urls, country, league):

  df = pd.DataFrame()

  for url in match_urls:
    
    driver.get(url)
    try:
      match_df = scrape_match_page(driver, country, league)
      df = pd.concat([match_df, df], sort=False, ignore_index=True).fillna(np.nan)
    except:
      print('Could not scrap match (ERROR line ~110):', str(url))
  return df

def get_match_urls(driver):
  tournamentTable = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id =" + '"tournamentTable"' + "]")))
  links = tournamentTable.find_elements_by_tag_name("a")
  urls = []

  for link in (links):
    link_str = str(link.get_attribute('href'))
    if link_str.count('/') > 6:
      urls.append(link_str)

  return urls

def combine_upcoming_and_old(upcoming, country, league):
  premier_league_df = read_odds(countries=country, leagues=league)
  premier_league_df = remove_nan_vals(premier_league_df)
  premier_league_df["Date"] = [pd.to_datetime(x).date() for x in premier_league_df["Date"]]

  df = pd.concat([premier_league_df, upcoming], sort=False, ignore_index=True).fillna(np.nan)
  df = transform_odds_to_probs(df)
  df = drop_duplicates(df)
  df = drop_bookies(df)
  df = sort_odds_by_date(df)
  return df

def drop_features(df):
  # TODO: Drop more features? country? league? h_team? a_team?
  df = df.drop(['date', 'time', 'fthg', 'ftag', 'ht1hg', 'ht1ag', 'ht2hg', 'ht2ag'], axis=1)
  return df

def scrape_upcoming_matches(country='england', league='premier-league'):
  options = Options()
  options.headless = True
  options.add_argument('--window-size=2560,1400')
  options.add_argument('log-level=1')
  DRIVER_PATH = Path('./chromedriver/chromedriver.exe').absolute()
  driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

  url = "https://www.oddsportal.com/soccer/" + country + "/" + league + "/"
  driver.get(url)
  match_urls = get_match_urls(driver)
  matches_df = scrape_matches(driver, match_urls, country, league)

  driver.quit()

  return matches_df

if __name__ == "__main__":
  country, league = 'england', 'premier-league'

  upcoming_matches_df = scrape_upcoming_matches(country, league)
  print(upcoming_matches_df)

  df = combine_upcoming_and_old(upcoming_matches_df, country, league)
  print(df)

  df = calculate_features(df)
  print(df)

  df = drop_features(df)
  print(df)

  # Just checking
  # print(df.loc[((df['h_team'] == 'ManchesterUtd') & (df['a_team'] == 'ManchesterCity')) | ((df['h_team'] == 'ManchesterCity') & (df['a_team'] == 'ManchesterUtd'))])
