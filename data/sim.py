import random
import numpy as np

from .db_game_shots import get_shots_for_team, get_avg_shots_for_team
from .db_goalkeeper_xgoals import get_goalkeeper_for_team

def simulate_shot_outcome(shot, gk_modifier=0.0):
    """
    Simulates whether a shot results in a goal.

    Args:
        shot (dict): Shot row with 'shot_xg' field.
        gk_modifier (float): Adjustment factor based on goalkeeper PSxG overperformance (e.g., -0.1 reduces scoring chance).

    Returns:
        bool: True if goal scored, else False.
    """
    base_xg = shot['shot_xg']
    adjusted_xg = max(0.01, min(0.95, base_xg * (1.0 + gk_modifier)))
    return random.random() < adjusted_xg

def simulate_team_goals(team_id, opponent_id, season, mode="shot", exclude_penalties=True):
    if mode == "shot":
        shot_data = get_shots_for_team(team_id, season)
        if exclude_penalties:
            shot_data = [s for s in shot_data if s['pattern_of_play'] and s['pattern_of_play'].lower() != 'penalty']
        avg_shots_per_game = get_avg_shots_for_team(team_id, season)
        sample_size = max(1, int(random.gauss(avg_shots_per_game, 2)))
        sampled_shots = random.sample(shot_data, min(sample_size, len(shot_data)))

        gk_stats = get_goalkeeper_for_team(opponent_id, season)
        gk_modifier = 0.0
        if gk_stats and gk_stats['xgoals_gk_faced'] > 0:
            over = gk_stats['goals_minus_xgoals_gk']
            xg_faced = gk_stats['xgoals_gk_faced']
            gk_modifier = -1.0 * (over / xg_faced)

        goals = 0
        scorers = []

        for shot in sampled_shots:
            if simulate_shot_outcome(shot, gk_modifier):
                goals += 1
                scorers.append({
                    'player_id': shot['shooter_player_id'],
                    'xg': shot['shot_xg'],
                    'minute': shot['expanded_minute'],
                    'shot_type': (
                        "Header" if "head" in shot.keys() and shot["head"] else
                        "Through Ball" if "assist_through_ball" in shot.keys() and shot["assist_through_ball"] else
                        "Cross" if "assist_cross" in shot.keys() and shot["assist_cross"] else
                        "Open Play"
                    )
                })

        return goals, scorers

    elif mode == "poisson":
        # Same as before; scorers not tracked in this mode
        shot_data = get_shots_for_team(team_id, season)
        total_xg = sum(s['shot_xg'] for s in shot_data)
        total_games = len(set(s['game_id'] for s in shot_data))
        avg_xg_per_game = total_xg / total_games if total_games > 0 else 1.0

        gk_stats = get_goalkeeper_for_team(opponent_id, season)
        gk_modifier = 0.0
        if gk_stats and gk_stats['xgoals_gk_faced'] > 0:
            over = gk_stats['goals_minus_xgoals_gk']
            xg_faced = gk_stats['xgoals_gk_faced']
            gk_modifier = -1.0 * (over / xg_faced)

        adjusted_lambda = max(0.1, avg_xg_per_game * (1.0 + gk_modifier))
        return np.random.poisson(adjusted_lambda), []  # no scorers


def simulate_match(home_team_id, away_team_id, season, mode="shot"):
    home_goals, home_scorers = simulate_team_goals(home_team_id, away_team_id, season, mode=mode)
    away_goals, away_scorers = simulate_team_goals(away_team_id, home_team_id, season, mode=mode)

    return {
        'home_team_id': home_team_id,
        'away_team_id': away_team_id,
        'home_goals': home_goals,
        'away_goals': away_goals,
        'home_scorers': home_scorers,
        'away_scorers': away_scorers
    }

