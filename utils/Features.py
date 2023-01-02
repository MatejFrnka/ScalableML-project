import pandas as pd
import numpy as np
from trueskill import TrueSkill, Rating, rate_1vs1


'''
Add last close odds feature for each team and match
'''
def calculate_last_close_feature(df):
  teams = np.unique(np.array(df.H_team.tolist() + df.A_team.tolist()))
  lastOdds_dict = {}

  # Create lists for the 'to-be-created' columns
  h_lastOdds = []
  a_lastOdds = []

  for team1 in teams:
    for team2 in teams:
      if team1 != team2:
        lastOdds_dict[(team1, team2)] = 0
        lastOdds_dict[(team2, team1)] = 0

  #print(lastOdds_dict)

  for i in range(len(df)):
    h_team = df.iloc[i]['H_team']
    a_team = df.iloc[i]['A_team']

    hc_pinn = df.iloc[i]['HC_Pinnacle']
    ac_pinn = df.iloc[i]['AC_Pinnacle']

    # Update the winstreak lists
    if lastOdds_dict[(h_team, a_team)] == 0 and lastOdds_dict[(a_team, h_team)] == 0:
      h_lastOdds.append(hc_pinn)
      a_lastOdds.append(ac_pinn)
    else:
      h_lastOdds.append(lastOdds_dict[(h_team, a_team)])
      a_lastOdds.append(lastOdds_dict[(a_team, h_team)])


    # Update the dict for this game below :)
    lastOdds_dict[(h_team, a_team)] = hc_pinn
    lastOdds_dict[(a_team, h_team)] = ac_pinn

  df['H_LastOdds'] = h_lastOdds
  df['A_LastOdds'] = a_lastOdds

  return df




'''
Add win streak for each team
'''
def calculate_win_streak_feature(df):
  teams = np.unique(np.array(df.H_team.tolist() + df.A_team.tolist()))
  winstreak_dict = {}

  # Create lists for the 'to-be-created' columns
  h_winstreak = []
  a_winstreak = []

  for team in teams:
    winstreak_dict[team] = 0

  for i in range(len(df)):
    h_team = df.iloc[i]['H_team']
    a_team = df.iloc[i]['A_team']

    # Update the winstreak lists
    h_winstreak.append(winstreak_dict[h_team])
    a_winstreak.append(winstreak_dict[a_team])

    # Update the dict for this game below :)

    hg = df.iloc[i]['FTHG']
    ag = df.iloc[i]['FTAG']

    h_prev = winstreak_dict.get(h_team)
    a_prev = winstreak_dict.get(a_team)

    # If home won
    if hg > ag:

      # Update loser
      if a_prev > 0:
        winstreak_dict[a_team] = -1
      else:
        winstreak_dict[a_team] = a_prev -1

      # Update winner
      if h_prev < 0:
        winstreak_dict[h_team] = 1
      else:
        winstreak_dict[h_team] = h_prev + 1

    # If away won
    elif ag > hg:

      # Update loser
      if h_prev > 0:
        winstreak_dict[h_team] = -1
      else:
        winstreak_dict[h_team] = h_prev -1

      # Update winner
      if a_prev < 0:
        winstreak_dict[a_team] = 1
      else:
        winstreak_dict[a_team] = a_prev + 1

  df['H_winstreak'] = h_winstreak
  df['A_winstreak'] = a_winstreak

  return df


'''
Add shock feature for each team and match
'''
def calculate_shock_feature(df, num_matches=1, count_type='sum'):

  teams = np.unique(np.array(df.H_team.tolist() + df.A_team.tolist()))
  shock_dict = {}
  # Create lists for the 'to-be-created' columns
  h_shocks = []
  a_shocks = []

  for team in teams:
    shock_dict[team] = [0]
  
  for i in range(len(df)):
    h_team = df.iloc[i]['H_team']
    a_team = df.iloc[i]['A_team']

    h_team_shocks = shock_dict[h_team]
    a_team_shocks = shock_dict[a_team]

    # Update the winstreak lists
    h_sum = np.sum(h_team_shocks[-num_matches:])
    a_sum = np.sum(a_team_shocks[-num_matches:])
    if count_type == 'sum':
      h_shocks.append(h_sum)
      a_shocks.append(a_sum)
    elif count_type == 'mean':
      h_shocks.append(h_sum/num_matches)
      a_shocks.append(a_sum/num_matches)
    else:
      raise Exception("ERROR, faulty 'count_type' entered!")

    # Update the dict for this game below :)
    hg = df.iloc[i]['FTHG']
    ag = df.iloc[i]['FTAG']

    hc_pinn = df.iloc[i]['HC_Pinnacle']
    ac_pinn = df.iloc[i]['AC_Pinnacle']

    if hg == ag:
      if hc_pinn > ac_pinn:
        h_team_shocks.append(-hc_pinn)
        a_team_shocks.append(ac_pinn)
      else:
        h_team_shocks.append(hc_pinn)
        a_team_shocks.append(-ac_pinn)
    else:
      h_team_shocks.append((hg * (1 - hc_pinn)) - (ag * (1 - ac_pinn)))
      a_team_shocks.append((ag * (1 - ac_pinn)) - (hg * (1 - hc_pinn)))

    shock_dict[h_team] = h_team_shocks
    shock_dict[a_team] = a_team_shocks
    # shock_dict[h_team] = (hg - ag) * (1 - hc_pinn)
    # shock_dict[a_team] = (ag - hg) * (1 - ac_pinn)

  df['H_' + str(num_matches) + 'shock'] = h_shocks
  df['A_'  + str(num_matches) + 'shock'] = a_shocks

  return(df)

  

'''
Add FTR from last game feature for each team and match
'''
def calculate_last_ftr_feature(df):
  teams = np.unique(np.array(df.H_team.tolist() + df.A_team.tolist()))
  lastFTG_dict = {}

  # Create lists for the 'to-be-created' columns
  h_lastFTG = []
  a_lastFTG = []

  for team1 in teams:
    for team2 in teams:
      if team1 != team2:
        lastFTG_dict[(team1, team2)] = 0
        lastFTG_dict[(team2, team1)] = 0

  for i in range(len(df)):
    h_team = df.iloc[i]['H_team']
    a_team = df.iloc[i]['A_team']

    # Update the winstreak lists
    h_lastFTG.append(lastFTG_dict[(h_team, a_team)])
    a_lastFTG.append(lastFTG_dict[(a_team, h_team)])

    # Update the dict for this game below :)

    fthg = df.iloc[i]['FTHG']
    ftag = df.iloc[i]['FTAG']

    lastFTG_dict[(h_team, a_team)] = fthg
    lastFTG_dict[(a_team, h_team)] = ftag
  
  df['H_LastFTG'] = h_lastFTG
  df['A_LastFTG'] = a_lastFTG

  return df



def calculate_mmr_feature(df, draw_probability=0.265, home_advantage = 1.3):
  teams = np.unique(np.array(df.H_team.tolist() + df.A_team.tolist()))

  trueSkill_env = TrueSkill(draw_probability=draw_probability)
  trueSkill_dict = {}

  # Add all teams to TrueSkill\n",
  for team in teams:
    trueSkill_dict[team] = trueSkill_env.create_rating()

  # Create lists for the 'to-be-created' columns
  h_mmr = []
  a_mmr = []

  for i in range(len(df)):
    h_team = df.iloc[i]['H_team']
    a_team = df.iloc[i]['A_team']

    # Update the mmr lists
    og_h_trueskill = trueSkill_dict[h_team]
    og_a_trueskill = trueSkill_dict[a_team]

    h_trueskill = Rating(og_h_trueskill.mu + home_advantage, og_h_trueskill.sigma)
    a_trueskill = og_a_trueskill

    h_mmr.append(h_trueskill.mu)
    a_mmr.append(a_trueskill.mu)

    # Update the mmr dict for this game below :)
    fthg = df.iloc[i]['FTHG']
    ftag = df.iloc[i]['FTAG']

    # If home won
    if fthg > ftag:
      new_h_trueskill, a_trueskill = trueSkill_env.rate_1vs1(h_trueskill, a_trueskill, drawn=False)
    # If away won
    elif ftag > fthg:
      a_trueskill, new_h_trueskill = trueSkill_env.rate_1vs1(a_trueskill, h_trueskill, drawn=False)
    # Draw
    else:
      new_h_trueskill, a_trueskill = trueSkill_env.rate_1vs1(h_trueskill, a_trueskill, drawn=True)

    trueSkill_dict[h_team] = Rating(og_h_trueskill.mu + (new_h_trueskill.mu - h_trueskill.mu), new_h_trueskill.sigma)
    trueSkill_dict[a_team] = a_trueskill

  df['H_MMR'] = h_mmr
  df['A_MMR'] = a_mmr
  return df




def calculate_points_feature(df, num_matches=15):
  teams = np.unique(np.array(df.H_team.tolist() + df.A_team.tolist()))
  points_dict = {}

  # Create lists for the 'to-be-created' columns
  h_points = []
  a_points = []

  for team in teams:
    points_dict[team] = [0]

  for i in range(len(df)):
    h_team = df.iloc[i]['H_team']
    a_team = df.iloc[i]['A_team']

    # Update the points lists
    h_points.append(np.sum(points_dict[h_team][-num_matches:]))
    a_points.append(np.sum(points_dict[a_team][-num_matches:]))

    # Update the dict for this game below :)
    h_points_update = points_dict[h_team]
    a_points_update = points_dict[a_team]

    fthg = df.iloc[i]['FTHG']
    ftag = df.iloc[i]['FTAG']

    # If home won
    if fthg > ftag:
      h_points_update.append(3)
      a_points_update.append(0)
    # If away won
    elif ftag > fthg:
      h_points_update.append(0)
      a_points_update.append(3)
    # Draw
    else:
      h_points_update.append(1)
      a_points_update.append(1)

    points_dict[h_team] = h_points_update
    points_dict[a_team] = a_points_update

  df['H_'  + str(num_matches) + 'Points'] = h_points
  df['A_'  + str(num_matches) + 'Points'] = a_points
  return df



'''
Add realized EV feature to the given dataframe.
Realized EV is: +odds if team won a match or viceversa over a window of matches
'''
def calculate_realized_ev_feature(df, num_matches=5):
  teams = np.unique(np.array(df.H_team.tolist() + df.A_team.tolist()))
  ev_dict = {}

  # Create lists for the 'to-be-created' columns
  h_evs = []
  a_evs = []

  for team in teams:
    ev_dict[team] = [0]

  for i in range(len(df)):
    h_team = df.iloc[i]['H_team']
    a_team = df.iloc[i]['A_team']

    # Update the points lists
    h_evs.append(np.sum(ev_dict[h_team][-num_matches:]))
    a_evs.append(np.sum(ev_dict[a_team][-num_matches:]))

    # Update the dict for this game below :)
    h_ev_update = ev_dict[h_team]
    a_ev_update = ev_dict[a_team]

    fthg = df.iloc[i]['FTHG']
    ftag = df.iloc[i]['FTAG']

    hc_prob = df.iloc[i]['HC_Pinnacle']
    ac_prob = df.iloc[i]['AC_Pinnacle']

    # If home won
    if fthg > ftag:
      h_ev_update.append(hc_prob)
      a_ev_update.append(-(1 - ac_prob))
    # If away won
    elif ftag > fthg:
      h_ev_update.append(-(1 - hc_prob))
      a_ev_update.append(ac_prob)
    # Draw
    else:
      h_ev_update.append(-(1 - hc_prob))
      a_ev_update.append(-(1 - ac_prob))

    ev_dict[h_team] = h_ev_update
    ev_dict[a_team] = a_ev_update

  df['H_' + str(num_matches) + 'EVs'] = h_evs
  df['A_' + str(num_matches) + 'EVs'] = a_evs
  return df