import numpy as np
from sklearn.linear_model import LinearRegression


class ExpectedGoals:
    def __init__(self, field_length=105, field_width=68, goal_width=7.32):
        """
        Initialize the xG model.
        :param field_length: Length of the pitch (in meters)
        :param field_width: Width of the pitch (in meters)
        :param goal_width: Width of the goal (in meters)
        """
        self.field_length = field_length
        self.field_width = field_width
        self.goal_width = goal_width
        self.goal_y_center = field_width / 2
        self.goal_x = field_length

    def calculate_shot_xg(self, x, y):
        """
        Calculate xG for a single shot based on coordinates.
        """
        distance = np.sqrt((self.goal_x - x) ** 2 + (self.goal_y_center - y) ** 2)
        try:
            angle = np.arctan((self.goal_width / 2) / distance)
        except ZeroDivisionError:
            angle = np.pi / 2
        xg = (np.degrees(angle) / 90) * (1 / (1 + distance / 5))
        return np.clip(xg, 0, 1)

    def calculate_match_xg(self, shots):
        total_xg = 0
        for shot in shots:
            x, y = shot
            total_xg += self.calculate_shot_xg(x, y)
        return total_xg

    def calculate_average_xg(self, matches_shots):
        all_xg = []
        for shots in matches_shots:
            match_xg = self.calculate_match_xg(shots)
            all_xg.append(match_xg)
        return np.mean(all_xg) if all_xg else 0

    def predict_future_xg(self, past_xg_array):
        if len(past_xg_array) == 0:
            return 0
        else:
            return np.mean(past_xg_array)

    def predict_trend_xg(self, past_xg_array):
        if len(past_xg_array) < 2:
            return self.predict_future_xg(past_xg_array)

        X = np.arange(len(past_xg_array)).reshape(-1, 1)
        y = np.array(past_xg_array)
        model = LinearRegression()
        model.fit(X, y)
        next_x = np.array([[len(past_xg_array)]])
        predicted_xg = model.predict(next_x)[0]

        return np.clip(predicted_xg, 0, None)


# === Example usage ===
"""
shots = [
    [90, 34],  # shot closer to goal from center
    [80, 30],  # shot from the wing
    [60, 40],  # long distance shot
]

# Create xG model object
xg_model = ExpectedGoals()

# Calculate total xG for the match
match_xg = xg_model.calculate_match_xg(shots)
print(f"Total xG for the match: {match_xg:.2f}")

# Example for multiple matches
matches = [
    shots,  # match 1
    [[85, 35], [70, 30], [65, 40]],  # match 2
    [[95, 34], [90, 32]]  # match 3
]

avg_xg = xg_model.calculate_average_xg(matches)
print(f"Average xG per match: {avg_xg:.2f}")

# Predict future match xG based on past xG
past_xg = [1.5, 1.7, 2.0, 1.6]
predicted_xg = xg_model.predict_future_xg(past_xg)
print(f"Predicted xG for next match (simple average): {predicted_xg:.2f}")

# Predict future match xG using trend
trend_predicted_xg = xg_model.predict_trend_xg(past_xg)
print(f"Predicted xG for next match (trend prediction): {trend_predicted_xg:.2f}")
"""
