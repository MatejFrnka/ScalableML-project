FW_VERSION = 5
FG_VERSION = 6
FW_UPCOMING_VERSION = 1
FG_UPCOMING_VERSION = 1

HomeTeam = 'h_team'  # H_team
AwayTeam = 'a_team'  # A_team
HomeCloseOdds = 'hc_pinnacle'  # HC_Pinnacle
AwayCloseOdds = 'ac_pinnacle'  # AC_Pinnacle
DrawCloseOdds = 'dc_pinnacle'  # DC_Pinnacle
HomeOpenOdds = 'ho_pinnacle'  # HO_Pinnacle
AwayOpenOdds = 'ao_pinnacle'  # AO_Pinnacle
DrawOpenOdds = 'do_pinnacle'  # DO_Pinnacle

FTHG = 'fthg'  # FTHG
FTAG = 'ftag'  # FTAG
H_LastOdds = 'h_lastodds'  # H_LastOdds
A_LastOdds = 'a_lastodds'  # A_LastOdds
H_winstreak = 'h_winstreak'  # H_winstreak
A_winstreak = 'a_winstreak'  # A_winstreak
H_LastFTG = 'h_lastftg'  # H_LastFTG
A_LastFTG = 'a_lastftg'  # A_LastFTG
H_MMR = 'h_mmr'  # H_MMR
A_MMR = 'a_mmr'  # A_MMR


def H_shock(num_matches): return 'h_' + str(num_matches) + 'shock'  # 'H_' + str(num_matches) + 'shock'


def A_shock(num_matches): return 'a_' + str(num_matches) + 'shock'  # 'A_' + str(num_matches) + 'shock'


def H_points(num_matches): return 'h_' + str(num_matches) + 'points'  # 'H_' + str(num_matches) + 'Points'


def A_points(num_matches): return 'a_' + str(num_matches) + 'points'  # 'A_' + str(num_matches) + 'Points'


def H_EVs(num_matches): return 'h_' + str(num_matches) + 'evs'  # 'H_' + str(num_matches) + 'EVs'


def A_EVs(num_matches): return 'a_' + str(num_matches) + 'evs'  # 'A_' + str(num_matches) + 'EVs'


# todo columns should take names from consts above
X_SCALE_COLUMNS = ['h_lastftg', 'a_lastftg',
                   'h_mmr', 'a_mmr', 'h_5points', 'a_5points', 'h_10points', 'a_10points', 'h_15points', 'a_15points',
                   'h_3evs', 'a_3evs', 'h_5evs', 'a_5evs', 'h_9evs', 'a_9evs', 'h_1shock', 'a_1shock', 'h_3shock',
                   'a_3shock', 'h_5shock', 'a_5shock', 'h_winstreak', 'a_winstreak']

Y_COLUMNS = ['hc_pinnacle', 'dc_pinnacle', 'ac_pinnacle']
X_COLUMNS = ['ao_pinnacle', 'a_lastodds', 'do_pinnacle', 'ho_pinnacle', 'h_lastodds', *X_SCALE_COLUMNS]
KEY_COLUMNS = ['h_team', 'a_team', 'date']
INFO_COLUMNS = ['fthg', 'ftag', 'league', 'country']
ALL_COLUMNS = [*Y_COLUMNS, *X_COLUMNS, *KEY_COLUMNS, *INFO_COLUMNS]
