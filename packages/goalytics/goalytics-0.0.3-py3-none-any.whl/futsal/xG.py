import numpy as np
from sklearn.linear_model import LinearRegression


class ExpectedGoalsFutsal:
    def __init__(self, field_length=40, field_width=20, goal_width=3):
        """
        Initialize the xG model for futsal.
        :param field_length: Length of the futsal pitch (default 40 meters)
        :param field_width: Width of the futsal pitch (default 20 meters)
        :param goal_width: Width of the futsal goal (default 3 meters)
        """
        self.field_length = field_length
        self.field_width = field_width
        self.goal_width = goal_width
        self.goal_y_center = field_width / 2
        self.goal_x = field_length  # Goal is located at the end of the field

    def calculate_shot_xg(self, x, y):
        """
        Calculate xG for a single futsal shot based on coordinates.
        :param x: X coordinate of the shot
        :param y: Y coordinate of the shot
        :return: xG value for the shot
        """
        distance = np.sqrt((self.goal_x - x) ** 2 + (self.goal_y_center - y) ** 2)

        # Angle to goal center
        try:
            angle = np.arctan((self.goal_width / 2) / distance)
        except ZeroDivisionError:
            angle = np.pi / 2  # Directly in front of goal

        # Futsal-specific xG calculation: higher importance to angle and proximity
        xg = (np.degrees(angle) / 45) * (1 / (1 + distance / 3))

        return np.clip(xg, 0, 1)

    def calculate_match_xg(self, shots):
        """
        Calculate total xG for a futsal match.
        :param shots: List of shots [[x1, y1], [x2, y2], ...]
        :return: Total xG for the match
        """
        total_xg = 0
        for shot in shots:
            x, y = shot
            total_xg += self.calculate_shot_xg(x, y)
        return total_xg

    def calculate_average_xg(self, matches_shots):
        """
        Calculate average xG across multiple futsal matches.
        :param matches_shots: List of shot lists for each match
        :return: Average xG per match
        """
        all_xg = []
        for shots in matches_shots:
            match_xg = self.calculate_match_xg(shots)
            all_xg.append(match_xg)
        return np.mean(all_xg) if all_xg else 0

    def predict_future_xg(self, past_xg_array):
        """
        Predict future xG based on simple average of past futsal matches.
        :param past_xg_array: List of past match xG values
        :return: Predicted xG for the next match
        """
        if len(past_xg_array) == 0:
            return 0
        else:
            return np.mean(past_xg_array)

    def predict_trend_xg(self, past_xg_array):
        """
        Predict future xG using linear regression trend from past futsal matches.
        :param past_xg_array: List of past match xG values
        :return: Trend-predicted xG for the next match
        """
        if len(past_xg_array) < 2:
            return self.predict_future_xg(past_xg_array)

        X = np.arange(len(past_xg_array)).reshape(-1, 1)
        y = np.array(past_xg_array)
        model = LinearRegression()
        model.fit(X, y)
        next_x = np.array([[len(past_xg_array)]])
        predicted_xg = model.predict(next_x)[0]

        return np.clip(predicted_xg, 0, None)


"""
shots = [
    [35, 10],  # Close center shot
    [30, 5],   # Shot from right side
    [25, 15]   # Longer distance shot
]

xg_model = ExpectedGoalsFutsal()

match_xg = xg_model.calculate_match_xg(shots)
print(f"Total xG for the futsal match: {match_xg:.2f}")

matches = [
    shots,
    [[34, 8], [28, 12], [22, 10]],
    [[38, 9], [32, 6]]
]

avg_xg = xg_model.calculate_average_xg(matches)
print(f"Average xG per futsal match: {avg_xg:.2f}")

past_xg = [2.1, 1.8, 2.3, 2.0]
predicted_xg = xg_model.predict_future_xg(past_xg)
print(f"Predicted xG for next match (simple average): {predicted_xg:.2f}")

trend_predicted_xg = xg_model.predict_trend_xg(past_xg)
print(f"Predicted xG for next match (trend prediction): {trend_predicted_xg:.2f}")
"""
