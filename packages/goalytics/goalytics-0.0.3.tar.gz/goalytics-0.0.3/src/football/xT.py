import numpy as np
from sklearn.linear_model import LinearRegression


class ExpectedThreat:
    def __init__(self, field_length=105, field_width=68, x_bins=12, y_bins=8):
        """
        Initialize the xT model.
        """
        self.field_length = field_length
        self.field_width = field_width
        self.x_bins = x_bins
        self.y_bins = y_bins
        # Generate a simple threat grid (higher threat closer to goal)
        self.threat_grid = self._generate_threat_grid()

    def _generate_threat_grid(self):
        grid = np.zeros((self.x_bins, self.y_bins))
        for i in range(self.x_bins):
            for j in range(self.y_bins):
                grid[i, j] = (i / self.x_bins) * (
                    1 - abs(j - self.y_bins / 2) / (self.y_bins / 2)
                )
        grid /= grid.max()  # Normalize between 0 and 1
        return grid

    def _get_cell(self, x, y):
        x_idx = min(int(x / self.field_length * self.x_bins), self.x_bins - 1)
        y_idx = min(int(y / self.field_width * self.y_bins), self.y_bins - 1)
        return x_idx, y_idx

    def calculate_action_xt(self, start_x, start_y, end_x, end_y):
        start_cell = self._get_cell(start_x, start_y)
        end_cell = self._get_cell(end_x, end_y)
        start_threat = self.threat_grid[start_cell]
        end_threat = self.threat_grid[end_cell]
        return end_threat - start_threat

    def calculate_match_xt(self, actions):
        total_xt = 0
        for action in actions:
            start_x, start_y, end_x, end_y = action
            total_xt += self.calculate_action_xt(start_x, start_y, end_x, end_y)
        return total_xt

    def calculate_average_xt(self, matches_actions):
        all_xt = []
        for actions in matches_actions:
            match_xt = self.calculate_match_xt(actions)
            all_xt.append(match_xt)
        return np.mean(all_xt) if all_xt else 0


"""
actions = [
    [30, 20, 50, 30],
    [50, 30, 80, 34],
    [80, 34, 90, 34]
]

xt_model = ExpectedThreat()
match_xt = xt_model.calculate_match_xt(actions)
print(f"Total xT for the match: {match_xt:.2f}")

matches_actions = [
    actions,
    [[20, 10, 40, 20], [40, 20, 70, 30]],
    [[10, 5, 50, 30]]
]

avg_xt = xt_model.calculate_average_xt(matches_actions)
print(f"Average xT per match: {avg_xt:.2f}")
"""
