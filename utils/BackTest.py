import numpy as np


class Games:
    def __init__(self, home, draw, away):
        """
        Input 3 arrays, generally should be used for percentage of chance for home win, draw and away win.
        :param home: Array for home values, one entry = one game
        :param draw: Array for draw values, one entry = one game
        :param away: Array for away values, one entry = one game
        """
        self.home = home
        self.draw = draw
        self.away = away

    def get_normalized(self):
        """
        Normalizes entries so that entry.home + entry.draw + entry.away = 1
        :return: Games object with normalized values home, draw and away
        """
        total = self.home + self.draw + self.away
        return Games(self.home / total, self.draw / total, self.away / total)

    def get_odds(self):
        """
        Transforms object to odds if it contains percentages, and to percentages if it contains odds. Formula: 1/values
        :return: new Games object with transformed values
        """
        return Games(1 / self.home, 1 / self.draw, 1 / self.away)


class Evaluator:
    def __init__(self, buy_margin):
        self.margin = buy_margin

    def buy_function(self, diff_h, diff_d, diff_a):
        """
        Returns a three field array saying if and on what we should bet
        :param diff_h: predicted - actual win percentage for home team
        :param diff_d: predicted - actual win percentage for draw
        :param diff_a: predicted - actual win percentage for away team
        :param margin: minimum difference between predicted and actual to return a buy signal. Eg, if margin is 0.05, we predict home team win to 0.5 and the offered chance is 0.47, we still dont buy because the margin is 0.03, which is less than 0.05
        :return: [True/False, True/False, True/False] array. The 3 field arrays represent buy signal for home, draw, away. Meaning if the array has the following values: [False, False, True], we should bet on away team.
        """
        max = np.argmax([diff_h, diff_d, diff_a])
        res = [False, False, False]
        if [diff_h, diff_d, diff_a][max] > self.margin:
            res[max] = True
        return res

    def generate_buy_signals(self, given_percentage, predicted_percentage):
        """

        :param given_percentage: Games object containing NOT NORMALIZED percentage (sum of home, draw, away > 1) offered by betting site (e.g. Pinnacle)
        :param predicted_percentage: Games object containing predicted outcomes
        :param margin: minimum difference between predicted and actual to return a buy signal. Eg, if margin is 0.05, we predict home team win to 0.5 and the offered chance is 0.47, we still dont buy because the margin is 0.03, which is less than 0.05
        :return: Returns Game object containing arrays of True/False for game.home, game.draw, game.away. If any of the arrays is True, it means we should be on given result.
        """

        diff_h = predicted_percentage.home - given_percentage.home
        diff_d = predicted_percentage.draw - given_percentage.draw
        diff_a = predicted_percentage.away - given_percentage.away

        # run the buy_function for every game,
        buy = [self.buy_function(*v) for v in zip(diff_h, diff_d, diff_a)]
        return Games(*[np.array(k) for k in zip(*buy)])

    @staticmethod
    def evaluate_buy_signals(home_goals, away_goals, odds, buy_sig):
        """
        :param home_goals: aray of goals scored by home team, one entry = one game
        :param away_goals: aray of goals scored by home team, one entry = one game
        :param odds: Games object with odds for home, draw, away. One entry in each category represents one game
        :param buy_sig: Games object with True/False for home, draw, away. One entry in each category represents one game
        :return: Dictionary with metrics
        """
        h_outcome = home_goals > away_goals
        d_outcome = home_goals == away_goals
        a_outcome = home_goals < away_goals

        h_win = ((h_outcome & buy_sig.home) * odds.home).sum()
        h_spent = buy_sig.home.sum()
        d_win = ((d_outcome & buy_sig.draw) * odds.draw).sum()
        d_spent = buy_sig.draw.sum()
        a_win = ((a_outcome & buy_sig.away) * odds.away).sum()
        a_spent = buy_sig.away.sum()

        total_spent = h_spent + d_spent + a_spent
        winning_bets = ((h_outcome & buy_sig.home).sum()
                        + (d_outcome & buy_sig.draw).sum()
                        + (a_outcome & buy_sig.away).sum())

        metrics = {
            "roi": float(h_win + d_win + a_win - total_spent),
            "bet_count": float(total_spent),
            "bet_winning": float(winning_bets),
            "bet_loosing": float(total_spent - winning_bets),
            "win_percentage": float(winning_bets / total_spent)
        }

        return metrics

# example usage:
# evaluator = Evaluator(0.05)
# open_percentage = Games(df_test["HO_Pinnacle"].array,
#                         df_test["DO_Pinnacle"].array,
#                         df_test["AO_Pinnacle"].array)
#
# predictions = model.predict(X_finetuning_test_scale)
# predicted_odds = Games(*predictions.T)
# buy_sig = evaluator.generate_buy_signals(open_percentage, predicted_odds)
# Evaluator.evaluate_buy_signals(df_test["FTHG"].array, df_test["FTAG"].array, open_percentage.get_odds(), buy_sig)
