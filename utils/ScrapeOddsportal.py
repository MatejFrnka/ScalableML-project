from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
from utils.Features import *
import numpy as np
from pathlib import Path
import pandas as pd
import time
import re
import os

from utils.OddsData import *

DRIVER_PATH = "chromedriver"
# DRIVER_PATH = Path('./chromedriver/chromedriver.exe').absolute()


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
        odds_data = odds_data.get_attribute("innerHTML").split('Opening odds:')[1].replace(
            '<strong>Click to BET NOW</strong>', '').replace('<br>', '')
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

    return open, close


def strip_day(date_str):
    return date_str.replace('Monday, ', '').replace('Tuesday, ', '').replace('Wednesday, ', '').replace('Thursday, ',
                                                                                                        '').replace(
        'Friday, ', '').replace('Saturday, ', '').replace('Sunday, ', '').replace('Yesterday, ', '').replace('Today, ',
                                                                                                             '').replace(
        'Tomorrow, ', '')


def get_meta_data(driver, country, league, results=True):
    # time.sleep(1)
    teams = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id =" + '"col-content"' + "]/h1"))).text.split(' - ')
    H_team, A_team = teams[0].replace(' ', ''), teams[1].replace(' ', '')

    # time.sleep(1)
    date_str = strip_day(WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id =" + '"col-content"' + "]/p"))).text)
    date = datetime.strptime(date_str, '%d %b %Y, %H:%M')

    if results:
        results = driver.find_element_by_xpath("//*[@id =" + '"col-content"' + "]/div/p").text.replace('Final result ',
                                                                                                       '').replace('(',
                                                                                                                   '').replace(
            ')', '').replace(',', '').split(' ')
        FTHG, FTAG = int(results[0].split(':')[0]), int(results[0].split(':')[1])
        HT1HG, HT1AG = int(results[1].split(':')[0]), int(results[1].split(':')[1])
        HT2HG, HT2AG = int(results[2].split(':')[0]), int(results[2].split(':')[1])

        dict = {'country': [country], 'league': [league], 'h_team': [H_team],
                'a_team': [A_team], 'date': [date.date()], 'time': [date.time()],
                'fthg': [FTHG], 'ftag': [FTAG], 'ht1hg': [HT1HG], 'ht1ag': [HT1AG],
                'ht2hg': [HT2HG], 'ht2ag': [HT2AG]}
    else:
        dict = {'country': [country], 'league': [league], 'h_team': [H_team],
                'a_team': [A_team], 'date': [date.date()], 'time': [date.time()]}

    # PRINTS
    # print(H_team + ' - ' + A_team)
    # print(datetime_obj)
    # print(FTHG + ':' + FTAG + ' (' + HT1HG + ':' + HT1AG + ', ' + HT2HG + ':' + HT2AG + ')')

    return dict


def complete_dict(driver, dict, bookie, home, draw, away):
    b = bookie
    H_open, H_close = extract_open_close_odds(driver, home)
    D_open, D_close = extract_open_close_odds(driver, draw)
    A_open, A_close = extract_open_close_odds(driver, away)
    new_dict = {'HO_' + b: [H_open], 'DO_' + b: [D_open], 'AO_' + b: [A_open],
                'HC_' + b: [H_close], 'DC_' + b: [D_close], 'AC_' + b: [A_close]}

    dict.update(new_dict)
    return dict


def scrape_match_page(driver, country, league, results=True):
    dict = get_meta_data(driver, country, league, results)

    odds_data_table = driver.find_elements_by_xpath("//*[@id =" + '"odds-data-table"' + "]/div[1]/table/tbody/tr")
    num_rows = len(odds_data_table)

    print('Reading odds for ' + str(dict['h_team'][0]) + ' - ' + str(dict['a_team'][0]) + '...')

    for index in (range(1, num_rows)):
        row_data = driver.find_elements_by_xpath(
            "//*[@id =" + '"odds-data-table"' + "]/div[1]/table/tbody/tr[" + str(index) + "]/td")
        bookie, home, draw, away = row_data[0].text.replace(' ', ''), row_data[1], row_data[2], row_data[3]
        dict = complete_dict(driver, dict, bookie, home, draw, away)

    if results:
        exch_odds_data_table = driver.find_elements_by_xpath(
            "//*[@id =" + '"odds-data-table"' + "]/div[3]/table/tbody/tr")
        num_rows = len(exch_odds_data_table)

        # time.sleep(2)

        for index in (range(1, num_rows)):
            # print('exchange#:', index)
            row_data = driver.find_elements_by_xpath(
                "//*[@id =" + '"odds-data-table"' + "]/div[3]/table/tbody/tr[" + str(index) + "]/td")
            bookie, home2, draw2, away2 = row_data[0].text.replace(' ', ''), row_data[2], row_data[3], row_data[4]
            dict = complete_dict(driver, dict, bookie, home2, draw2, away2)

    df = pd.DataFrame(dict)
    return df


def scrape_matches(driver, match_urls, country, league, stop_at=None, results=True):
    df = pd.DataFrame()
    for url in match_urls:
        driver.get(url)
        try:
            meta_data = get_meta_data(driver, country, league, results)
            # If we are scraping historic results
            if results:
                # Check that the match is in the past
                if meta_data['date'][0] < datetime.now().date():
                    match_df = scrape_match_page(driver, country, league, results)
                    # If stop_at is not None, but a DF
                    if isinstance(stop_at, pd.DataFrame):
                        # If we found the match we should stop at
                        if (match_df['h_team'].values[0] == stop_at['h_team'].values[0]) and \
                                (match_df['a_team'].values[0] == stop_at['a_team'].values[0]) and \
                                (str(match_df['date'].values[0]) == str(stop_at['date'].values[0])):
                            return df, True
            # If we are scraping upcoming matches
            else:
                match_df = scrape_match_page(driver, country, league, results)

            df = pd.concat([match_df, df], sort=False, ignore_index=True).fillna(np.nan)
        except Exception as e:
            print('Could not scrape match:', str(url))
    return df, False


def get_page_urls(driver):
    # time.sleep(1)
    years_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class =" + '"main-menu2 main-menu-gray"' + "]")))
    links = years_element.find_elements_by_tag_name("a")
    urls = []
    for link in (links):
        urls.append(str(link.get_attribute('href')))
    return urls


def get_match_urls(driver, results=True):
    # time.sleep(2)
    if results:
        tournamentTable = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id =" + '"tournamentTable"' + "]/table/tbody")))
    else:
        tournamentTable = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id =" + '"tournamentTable"' + "]")))
    links = tournamentTable.find_elements_by_tag_name("a")
    urls = []

    for link in (links):
        link_str = str(link.get_attribute('href'))
        if link_str.count('/') > 6:
            urls.append(link_str)

    return urls


def get_sub_page_urls(driver):
    try:
        tournamentTable = driver.find_element_by_xpath("//*[@id =" + '"tournamentTable"' + "]/div[1]")
        links = tournamentTable.find_elements_by_tag_name("a")
        urls = []
        for link in (links):
            if link.get_attribute('href') not in urls:
                urls.append(link.get_attribute('href'))

        return urls

    except NoSuchElementException:
        return [driver.current_url]


def file_exists(country, league):
    paths = get_all_paths()
    for path in paths:
        if (country + '/' + league) in path:
            return True

    return False


def get_path(country, league):
    paths = get_all_paths()
    for path in paths:
        if (country + '/' + league) in path:
            return path
    return None


def get_all_countries_and_leagues():
    paths = get_all_paths()
    countries_and_leagues = []
    for path in paths:
        country_and_league = path.split('/')[-2:]
        country_and_league[1] = country_and_league[1].split('_')[0]
        countries_and_leagues.append(country_and_league)

    return countries_and_leagues


def update_league_results(country, league):
    old_df = read_odds(countries=country, leagues=league)
    latest_match_df = old_df[-1:]
    print('Stopping at:', latest_match_df['H_team'], latest_match_df['A_team'], latest_match_df['Date'])

    new_df = scrape_historical_league(country, league, stop_at=latest_match_df)
    new_df = pd.concat([old_df, new_df], sort=False, ignore_index=True).fillna(np.nan)
    new_df = drop_duplicates(new_df)

    base_path = './data/soccer/historical/' + country + '/'
    file_name = league + '_' + str(datetime.now().date()) + '.csv'

    new_df.to_csv(os.path.join(base_path, file_name))


def update_all_leagues():
    countries_and_leagues = get_all_countries_and_leagues()
    for [country, league] in countries_and_leagues:
        print('Updating results for:', country, league)
        update_league_results(country, league)


def scrape_upcoming_matches(country='england', league='premier-league'):
    driver = get_driver()
    driver = login(driver)

    url = "https://www.oddsportal.com/soccer/" + country + "/" + league + "/"
    driver.get(url)
    match_urls = get_match_urls(driver, results=False)
    matches_df, stop = scrape_matches(driver, match_urls, country, league, stop_at=None, results=False)

    driver.quit()

    return matches_df


def combine_upcoming_and_old(upcoming, country, league, old_df):
    old_df["date"] = [pd.to_datetime(x).date() for x in old_df["date"]]

    df = pd.concat([old_df, upcoming], sort=False, ignore_index=True).fillna(np.nan)
    df = transform_odds_to_probs(df)
    df = drop_duplicates(df)
    df = drop_bookies(df)
    df = sort_odds_by_date(df)
    return df


def scrape_historical_league(country, league, stop_at=None):
    base_path = './data/soccer/historical/' + country + '/'
    file_name = league + '_' + str(datetime.now().date()) + '.csv'
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    driver = get_driver()
    driver = login(driver)

    start_url = 'https://www.oddsportal.com/soccer/' + country + '/' + league + '/results/'
    driver.get(start_url)

    page_urls = get_page_urls(driver)
    df = pd.DataFrame()

    for index1, url in enumerate(page_urls):

        if index1 != 0:
            driver.get(url)

        sub_pages = get_sub_page_urls(driver)

        for index2, sub_url in enumerate(sub_pages):

            print('-------Scraping page ' + str(index1 + 1) + '.' + str(index2 + 1) + '-------')
            print(sub_url)
            if index2 != 0:
                driver.get(sub_url)

            match_urls = get_match_urls(driver)
            matches_df, stop = scrape_matches(driver, match_urls, country, league, stop_at)

            df = pd.concat([matches_df, df], sort=False, ignore_index=True).fillna(np.nan)

            if stop:
                return df
            else:
                df.to_csv(os.path.join(base_path, file_name))
    driver.quit()
    return df


def get_driver():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.headless = True
    options.add_argument('--window-size=2560,1400')
    options.add_argument('log-level=1')
    driver = webdriver.Chrome(DRIVER_PATH, options=options)
    return driver


def scrape_upcoming(country, league, existing_matches):
    existing_matches = existing_matches[existing_matches['league'] == league]
    existing_matches = existing_matches[existing_matches['country'] == country]
    upcoming_matches_df = scrape_upcoming_matches(country, league)
    print(upcoming_matches_df)
    # upcoming_matches_df.to_csv("tmp.csv")
    # upcoming_matches_df = pd.read_csv("tmp.csv")
    upcoming_matches_df.columns = map(str.lower, upcoming_matches_df.columns)
    upcoming_matches_df["date"] = [pd.to_datetime(x).date() for x in upcoming_matches_df["date"]]
    # existing_matches = read_odds(leagues=league, countries=country)

    num_new_matches = len(upcoming_matches_df)

    df = combine_upcoming_and_old(upcoming_matches_df, country, league, existing_matches)
    print(df)

    df = calculate_features(df)
    print(df)

    df = df[-num_new_matches:].reset_index(drop=True)
    return df


def scrape_historical(country, league, historical_df):
    historical_df = historical_df.sort_values(by='date')
    historical_df = historical_df[historical_df['country'] == country]
    historical_df = historical_df[historical_df['league'] == league]
    latest_match_df = historical_df[-1:]

    new_df = scrape_historical_league(country, league, stop_at=latest_match_df)
    new_df.columns = map(str.lower, new_df.columns)
    new_df["date"] = [pd.to_datetime(x).date() for x in new_df["date"]]
    num_new_matches = len(new_df)

    df = combine_upcoming_and_old(new_df, country, league, historical_df)
    df = calculate_features(df)
    return df[-num_new_matches:].reset_index(drop=True)


if __name__ == "__main__":
    country, league = 'england', 'premier-league'
    # Scrape new data
    # df = scrape_historical_league(country, league)

    # Update an already existing dataframe

    # Update all existing dataframes
    update_all_leagues()

    # # Scrape upcoming matches and adding features
    # odds = read_odds(country, league)
    # upcoming = scrape_upcoming(country, league, odds)
    # print(upcoming)
