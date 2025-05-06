import numpy as np


class ExpectedAssistsFutsal:
    def __init__(self, field_length=40, field_width=20, goal_x=40, goal_y=10):
        """
        Futsal-oriented xA model.
        :param field_length: Pitch length in meters (default 40)
        :param field_width: Pitch width in meters (default 20)
        :param goal_x: X-coordinate of center of goal (default at far right)
        :param goal_y: Y-coordinate of goal center (default center height)
        """
        self.field_length = field_length
        self.field_width = field_width
        self.goal_x = goal_x
        self.goal_y = goal_y

    def estimate_xg(self, x, y):
        """
        Estimate xG based on shot location (x, y) using distance + angle heuristics.
        Closer and more central = higher xG.
        """
        dx = self.goal_x - x
        dy = abs(self.goal_y - y)
        distance = np.hypot(dx, dy)
        angle = np.arctan2(1.5, distance)  # simulate narrow angles in futsal
        xg = (1 / (1 + distance)) * angle * 5  # higher weighting for short distance
        return np.clip(xg, 0, 1)

    def pass_to_xa(self, x1, y1, x2, y2):
        """
        Estimate xA for a single pass using the end location (x2, y2).
        """
        xg = self.estimate_xg(x2, y2)
        return xg  # in simple models: xA = resulting xG

    def calculate_total_xa(self, passes):
        """
        Compute total xA for all passes.
        :param passes: List of (x1, y1, x2, y2) passes
        """
        return sum(self.pass_to_xa(*p) for p in passes)

    def calculate_average_xa(self, match_passes):
        """
        Compute average xA over multiple matches.
        :param match_passes: List of lists of passes [(x1, y1, x2, y2), ...] per match
        """
        match_xa = [self.calculate_total_xa(passes) for passes in match_passes]
        return np.mean(match_xa) if match_xa else 0
    
"""
xa_model = ExpectedAssistsFutsal()

passes = [
    (10, 5, 35, 10),  # diagonal pass into center
    (20, 4, 38, 11),  # side to far post
    (18, 10, 39, 10)  # central cut-back
]

print(f"Total xA: {xa_model.calculate_total_xa(passes):.2f}")
"""
