from data import sim

# simulator = sim.MatchSimulator('aDQ0lzvQEv', 'zeQZeazqKw', 2025, mode="shot")
simulator = sim.MatchSimulator('aDQ0lzvQEv', 'zeQZeazqKw', 2025, mode="shot", use_psxg=True)

simulator.run_simulations(100)


scorelines = simulator.get_scoreline_distribution()
for score, stats in scorelines.items():
    print(f"{score}: {stats['count']} times ({stats['pct']:.1%})")
home_scorers = simulator.get_top_scorers('home')
away_scorers = simulator.get_top_scorers('away')
summary = simulator.get_summary()

print(f"\nTop Scorers for {summary['home_team_name']}:")
for scorer in home_scorers:
    print(f"  {scorer['player_name']}: {scorer['goals']} goals")

print(f"\nTop Scorers for {summary['away_team_name']}:")
for scorer in away_scorers:
    print(f"  {scorer['player_name']}: {scorer['goals']} goals")


print(f"\n--- {summary['home_team_name']} vs {summary['away_team_name']} ({simulator.n_simulations} simulations, mode='{simulator.mode}') ---")
print(f"{summary['home_team_name']} Wins: {summary['home_win_pct']:.1%}")
print(f"Draws:     {summary['draw_pct']:.1%}")
print(f"{summary['away_team_name']} Wins: {summary['away_win_pct']:.1%}")
print(f"\nAvg Home Goals: {summary['avg_home_goals']:.2f}")
print(f"Avg Away Goals: {summary['avg_away_goals']:.2f}")

print("\n--- Match Analysis ---\n")
print(simulator.generate_analysis_paragraphs())
