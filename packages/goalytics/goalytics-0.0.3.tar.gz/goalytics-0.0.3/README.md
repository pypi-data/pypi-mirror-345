# goalytics

Goalytics is a modern Python library designed for advanced football analytics, focused on calculating and predicting key performance metrics like xG (Expected Goals), xA (Expected Assists), and xT (Expected Threat). 

- football
    - xG
    - xA
    - xT
- futsal
    - xG
    - xA
    - xT

### Example

```bash
pip install goalytics
```

```python
from goalytics.football.xG import ExpectedGoals

shots = [
    [90, 34],
    [80, 30],
    [60, 40],
]

xg_model = ExpectedGoals()

match_xg = xg_model.calculate_match_xg(shots)
print(f"Total xG for the match: {match_xg:.2f}")
```
   
