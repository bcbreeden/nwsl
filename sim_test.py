from collections import Counter, defaultdict
from data import sim, db_player_info, db_team_info

home_team = 'aDQ0lzvQEv'
away_team = 'zeQZeazqKw'
season = 2025
n_simulations = 1000
mode = "shot"  # Use "shot" to track scorers

# Load mappings
player_name_map = db_player_info.get_player_name_map()
team_name_map = db_team_info.get_team_name_map()

# Tracking
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

    if mode == "shot":
        for scorer in result.get('home_scorers', []):
            scorer_totals[home_team][scorer['player_id']] += 1
        for scorer in result.get('away_scorers', []):
            scorer_totals[away_team][scorer['player_id']] += 1

# Final print summary
home_name = team_name_map.get(home_team, home_team)
away_name = team_name_map.get(away_team, away_team)

print(f"--- {home_name} vs {away_name} ({n_simulations} simulations, mode='{mode}') ---")
print(f"{home_name} Wins: {outcomes['home_win']} ({outcomes['home_win'] / n_simulations:.1%})")
print(f"Draws:            {outcomes['draw']} ({outcomes['draw'] / n_simulations:.1%})")
print(f"{away_name} Wins: {outcomes['away_win']} ({outcomes['away_win'] / n_simulations:.1%})")

# Scoreline distribution
print("\nAll scorelines:")
for (h, a), count in scorelines.most_common():
    print(f"  {home_name} {h} - {a} {away_name}: {count} times ({count / n_simulations:.1%})")

# Average goals
avg_home_goals = sum(goal_totals['home']) / n_simulations
avg_away_goals = sum(goal_totals['away']) / n_simulations
print(f"\nAvg Goals — {home_name}: {avg_home_goals:.2f}, {away_name}: {avg_away_goals:.2f}")

# Top scorers
if mode == "shot":
    print(f"\nTop scorers for {home_name}:")
    for player_id, count in scorer_totals[home_team].most_common(10):
        name = player_name_map.get(player_id, f"[{player_id}]")
        print(f"  {name}: {count} goals")

    print(f"\nTop scorers for {away_name}:")
    for player_id, count in scorer_totals[away_team].most_common(10):
        name = player_name_map.get(player_id, f"[{player_id}]")
        print(f"  {name}: {count} goals")
