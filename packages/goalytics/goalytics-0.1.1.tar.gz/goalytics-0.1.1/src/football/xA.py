import numpy as np


class ExpectedAssists:
    def __init__(self):
        """
        Initialize the xA model.
        """
        pass

    def calculate_pass_xa(self, shot_xg):
        """
        Calculate xA for a single pass based on resulting shot's xG.
        :param shot_xg: xG value of the shot following the pass
        :return: xA value for the pass
        """
        return np.clip(shot_xg, 0, 1)

    def calculate_match_xa(self, passes_shot_xg):
        """
        Calculate total xA for a match.
        :param passes_shot_xg: List of xG values from shots following passes
        :return: total xA for the match
        """
        total_xa = sum(self.calculate_pass_xa(shot_xg) for shot_xg in passes_shot_xg)
        return total_xa

    def calculate_average_xa(self, matches_passes_shot_xg):
        """
        Calculate average xA across multiple matches.
        :param matches_passes_shot_xg: List of lists of shot xG values for each match
        :return: average xA per match
        """
        all_xa = []
        for passes_shot_xg in matches_passes_shot_xg:
            match_xa = self.calculate_match_xa(passes_shot_xg)
            all_xa.append(match_xa)

        if len(all_xa) == 0:
            return 0
        else:
            return np.mean(all_xa)


"""
passes = [0.3, 0.2, 0.7]
xa_model = ExpectedAssists()
match_xa = xa_model.calculate_match_xa(passes)
print(f"Total xA for the match: {match_xa:.2f}")

matches_passes = [
    [0.4, 0.1, 0.5],
    [0.6, 0.3]
]

avg_xa = xa_model.calculate_average_xa(matches_passes)
print(f"Average xA per match: {avg_xa:.2f}")
"""
