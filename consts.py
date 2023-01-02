X_SCALE_COLUMNS = ['h_lastftg', 'a_lastftg',
                   'h_mmr', 'a_mmr', 'h_5points', 'a_5points', 'h_10points', 'a_10points', 'h_15points', 'a_15points',
                   'h_3evs', 'a_3evs', 'h_5evs', 'a_5evs', 'h_9evs', 'a_9evs', 'h_1shock', 'a_1shock', 'h_3shock',
                   'a_3shock', 'h_5shock', 'a_5shock', 'h_winstreak', 'a_winstreak']

Y_COLUMNS = ['hc_pinnacle', 'dc_pinnacle', 'ac_pinnacle']
X_COLUMNS = ['ao_pinnacle', 'a_lastodds', 'do_pinnacle', 'ho_pinnacle', 'h_lastodds', *X_SCALE_COLUMNS]
KEY_COLUMNS = ['h_team', 'a_team', 'date']
INFO_COLUMNS = ['fthg', 'ftag', 'league', 'country']
ALL_COLUMNS = [*Y_COLUMNS, *X_COLUMNS, *KEY_COLUMNS, *INFO_COLUMNS]

FW_VERSION = 5
FG_VERSION = 5
