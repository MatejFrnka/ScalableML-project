import math

import numpy as np


class EloCalculator:
    # https://www.researchgate.net/publication/309662241_Mathematical_Model_of_Ranking_Accuracy_and_Popularity_Promotion

    def __init__(self, home_advantage=75, k=40):
        self.home_advantage = home_advantage
        self.k = k

    def update(self, home_team, away_team, home_score, away_score, teams):
        def get_win(score, enemy_score):
            if score > enemy_score:
                return 1
            elif score == enemy_score:
                return 0.5
            return 0

        def get_g(h_score, a_score):
            goal_diff = math.fabs(h_score - a_score)
            if goal_diff <= 1:
                return 1
            if goal_diff == 2:
                return 1.5
            return (11 + goal_diff) / 8

        def get_expected(h_score, a_score, is_home):
            dr = h_score + self.home_advantage - a_score
            if is_home:
                dr *= -1
            return 1 / (1 + 10 ** (dr / 400))

        home_win = get_win(home_score, away_score)
        away_win = get_win(away_score, home_score)
        home_expected = get_expected(teams[home_team], teams[away_team], True)
        away_expected = get_expected(teams[home_team], teams[away_team], False)
        # todo, update k based on tournament type
        new_elo_home = teams[home_team] + self.k * get_g(home_score, away_score) * (home_win - home_expected)
        new_elo_away = teams[away_team] + self.k * get_g(home_score, away_score) * (away_win - away_expected)
        teams[home_team] = new_elo_home
        teams[away_team] = new_elo_away

    def get_dr(self, home_team, away_team, teams):
        return (teams[home_team] + self.home_advantage) - teams[away_team]

    def draw_odds(self, home_team, away_team, teams):
        dr = self.get_dr(home_team, away_team, teams)
        return (1 / math.sqrt(2 * math.pi * math.e)) * math.exp(-((dr / 200) ** 2) / (2 * math.exp(2)))

    def home_odds(self, home_team, away_team, teams):
        dr = self.get_dr(home_team, away_team, teams)
        return (1 / (1 + 10 ** (-dr / 400))) - (1 / 2) * self.draw_odds(home_team, away_team, teams)

    def away_odds(self, home_team, away_team, teams):
        dr = self.get_dr(home_team, away_team, teams)
        return (1 / (1 + 10 ** (dr / 400))) - (1 / 2) * self.draw_odds(home_team, away_team, teams)

    def predict(self, home_team, away_team, teams):
        home_rating = 10 ** ((teams[home_team] + self.home_advantage) / 400)
        away_rating = 10 ** ((teams[away_team]) / 400)
        home_expected_score = home_rating / (home_rating + away_rating)
        return home_expected_score


# e = EloCalculator(home_advantage=0)
# teams = {"a": 1400, "b": 1950}
# e.update("a", "b", 3, 0, teams)
# print(e.away_odds("a", "b", teams), e.draw_odds("a", "b", teams), e.home_odds("a", "b", teams))
