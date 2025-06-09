from collections import Counter, defaultdict
from data import sim

home_team = 'aDQ0lzvQEv'
away_team = 'zeQZeazqKw'
season = 2025
n_simulations = 100
mode = "shot"  # Use "shot" for scorer tracking

# Tracking results
scorelines = Counter()
outcomes = Counter()
goal_totals = defaultdict(list)
scorer_totals = defaultdict(Counter)  # {team_id: Counter({player_id: count})}

for _ in range(n_simulations):
    result = sim.simulate_match(
        home_team_id=home_team,
        away_team_id=away_team,
        season=season,
        mode=mode
    )

    h_goals = result['home_goals']
    a_goals = result['away_goals']
    scorelines[(h_goals, a_goals)] += 1
    goal_totals['home'].append(h_goals)
    goal_totals['away'].append(a_goals)

    if h_goals > a_goals:
        outcomes['home_win'] += 1
    elif h_goals < a_goals:
        outcomes['away_win'] += 1
    else:
        outcomes['draw'] += 1

    # Tally scorers if shot-based
    if mode == "shot":
        for scorer in result.get('home_scorers', []):
            scorer_totals[home_team][scorer['player_id']] += 1
        for scorer in result.get('away_scorers', []):
            scorer_totals[away_team][scorer['player_id']] += 1

# Print summary
print(f"--- {home_team} vs {away_team} ({n_simulations} simulations, mode='{mode}') ---")
print(f"Home Wins: {outcomes['home_win']} ({outcomes['home_win'] / n_simulations:.1%})")
print(f"Draws:     {outcomes['draw']} ({outcomes['draw'] / n_simulations:.1%})")
print(f"Away Wins: {outcomes['away_win']} ({outcomes['away_win'] / n_simulations:.1%})")
print("\nAll scorelines:")
for (h, a), count in scorelines.most_common():
    print(f"  {h}-{a}: {count} times ({count / n_simulations:.1%})")

# Average goals
avg_home_goals = sum(goal_totals['home']) / n_simulations
avg_away_goals = sum(goal_totals['away']) / n_simulations
print(f"\nAvg Home Goals: {avg_home_goals:.2f}")
print(f"Avg Away Goals: {avg_away_goals:.2f}")

# Top scorers
if mode == "shot":
    print(f"\nTop scorers for {home_team}:")
    for player_id, count in scorer_totals[home_team].most_common(10):
        print(f"  {player_id}: {count} goals")

    print(f"\nTop scorers for {away_team}:")
    for player_id, count in scorer_totals[away_team].most_common(10):
        print(f"  {player_id}: {count} goals")
