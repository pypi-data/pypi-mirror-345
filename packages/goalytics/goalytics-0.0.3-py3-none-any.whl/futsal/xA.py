import numpy as np


class ExpectedAssistsFutsal:
    def __init__(self, field_length=40, field_width=20):
        """
        Initialize the xA model optimized for futsal.
        :param field_length: Length of the futsal pitch (default 40 meters)
        :param field_width: Width of the futsal pitch (default 20 meters)
        """
        self.field_length = field_length
        self.field_width = field_width

    def calculate_pass_xa(self, shot_xg):
        """
        Calculate xA for a single pass based on the resulting shot's xG.
        :param shot_xg: xG value of the shot following the pass
        :return: xA value for the pass (clipped between 0 and 1)
        """
        return np.clip(shot_xg, 0, 1)

    def calculate_match_xa(self, passes_shot_xg):
        """
        Calculate total xA for a futsal match.
        :param passes_shot_xg: List of xG values from shots following passes
        :return: total xA for the match
        """
        total_xa = sum(self.calculate_pass_xa(shot_xg) for shot_xg in passes_shot_xg)
        return total_xa

    def calculate_average_xa(self, matches_passes_shot_xg):
        """
        Calculate average xA across multiple futsal matches.
        :param matches_passes_shot_xg: List of lists of shot xG values for each match
        :return: average xA per match
        """
        all_xa = []
        for passes_shot_xg in matches_passes_shot_xg:
            match_xa = self.calculate_match_xa(passes_shot_xg)
            all_xa.append(match_xa)

        return np.mean(all_xa) if all_xa else 0


"""
passes = [0.5, 0.6, 0.8]  # Typical futsal xG values after passes
xa_model = ExpectedAssistsFutsal()

match_xa = xa_model.calculate_match_xa(passes)
print(f"Total xA for the futsal match: {match_xa:.2f}")

matches_passes = [
    [0.4, 0.6, 0.7],
    [0.8, 0.5]
]
avg_xa = xa_model.calculate_average_xa(matches_passes)
print(f"Average xA per futsal match: {avg_xa:.2f}")
"""
