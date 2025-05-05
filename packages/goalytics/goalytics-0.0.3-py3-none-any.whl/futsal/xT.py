import numpy as np


class ExpectedThreatFutsal:
    def __init__(self, field_length=40, field_width=20, x_bins=10, y_bins=6):
        """
        Initialize the xT model optimized for futsal.
        :param field_length: Length of the futsal pitch (default 40 meters)
        :param field_width: Width of the futsal pitch (default 20 meters)
        :param x_bins: Number of bins along the field length
        :param y_bins: Number of bins along the field width
        """
        self.field_length = field_length
        self.field_width = field_width
        self.x_bins = x_bins
        self.y_bins = y_bins
        self.threat_grid = self._generate_threat_grid()

    def _generate_threat_grid(self):
        """
        Generate a basic threat grid for futsal.
        Higher values near the opponent's goal.
        """
        grid = np.zeros((self.x_bins, self.y_bins))
        for i in range(self.x_bins):
            for j in range(self.y_bins):
                # Faster threat increase in futsal: power function
                distance_to_goal = 1 - (i / (self.x_bins - 1))
                center_factor = 1 - (
                    abs(j - (self.y_bins - 1) / 2) / ((self.y_bins - 1) / 2)
                )
                threat = (distance_to_goal**1.5) * (center_factor**1.5)
                grid[i, j] = max(threat, 0)
        grid /= grid.max()  # Normalize between 0 and 1
        return grid

    def _get_cell(self, x, y):
        """
        Convert real coordinates into grid cells.
        """
        x_idx = min(int(x / self.field_length * self.x_bins), self.x_bins - 1)
        y_idx = min(int(y / self.field_width * self.y_bins), self.y_bins - 1)
        return x_idx, y_idx

    def calculate_action_xt(self, start_x, start_y, end_x, end_y):
        """
        Calculate xT gain for a single ball movement.
        """
        start_cell = self._get_cell(start_x, start_y)
        end_cell = self._get_cell(end_x, end_y)
        start_threat = self.threat_grid[start_cell]
        end_threat = self.threat_grid[end_cell]
        return end_threat - start_threat

    def calculate_match_xt(self, actions):
        """
        Calculate total xT for a match.
        :param actions: List of actions [start_x, start_y, end_x, end_y]
        """
        total_xt = 0
        for action in actions:
            start_x, start_y, end_x, end_y = action
            total_xt += self.calculate_action_xt(start_x, start_y, end_x, end_y)
        return total_xt

    def calculate_average_xt(self, matches_actions):
        """
        Calculate average xT across multiple matches.
        :param matches_actions: List of match actions
        """
        all_xt = []
        for actions in matches_actions:
            match_xt = self.calculate_match_xt(actions)
            all_xt.append(match_xt)
        return np.mean(all_xt) if all_xt else 0


"""
actions = [
    [20, 10, 30, 10],  # Pass forward
    [30, 10, 38, 9],   # Pass closer to goal
    [38, 9, 40, 10]    # Final pass very close to goal
]

xt_model = ExpectedThreatFutsal()
match_xt = xt_model.calculate_match_xt(actions)
print(f"Total xT for the futsal match: {match_xt:.2f}")

matches_actions = [
    actions,
    [[15, 5, 28, 10], [28, 10, 35, 12]],
    [[10, 5, 25, 8]]
]

avg_xt = xt_model.calculate_average_xt(matches_actions)
print(f"Average xT per futsal match: {avg_xt:.2f}")
"""
