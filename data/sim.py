import random
import numpy as np
from collections import Counter, defaultdict

from data.db_game_shots import get_shots_for_team, get_avg_shots_for_team
from data.db_goalkeeper_xgoals import get_goalkeeper_for_team
from data.db_player_info import get_player_name_map
from data.db_team_info import get_team_name_map
from data.db_team_xgoals import get_team_xga_per_game


class MatchSimulator:
    def __init__(self, home_team_id, away_team_id, season, mode="shot", exclude_penalties=True, use_psxg=False):
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id
        self.season = season
        self.mode = mode
        self.exclude_penalties = exclude_penalties
        self.n_simulations = 0
        self.use_psxg = use_psxg

        self.player_name_map = get_player_name_map()
        self.team_name_map = get_team_name_map()

        self.scorelines = Counter()
        self.outcomes = Counter()
        self.goal_totals = defaultdict(list)
        self.scorer_totals = defaultdict(Counter)

    def simulate_match(self):
        home_goals, home_scorers = self.simulate_team_goals(self.home_team_id, self.away_team_id)
        away_goals, away_scorers = self.simulate_team_goals(self.away_team_id, self.home_team_id)

        for pid in home_scorers:
            self.scorer_totals[self.home_team_id][pid] += 1
        for pid in away_scorers:
            self.scorer_totals[self.away_team_id][pid] += 1

        return home_goals, away_goals

    def simulate_team_goals(self, team_id, opponent_id):
        scorers = []
        goals = 0

        if self.mode == "shot":
            shots = get_shots_for_team(team_id, self.season)
            if self.exclude_penalties:
                shots = [s for s in shots if s["pattern_of_play"] and s["pattern_of_play"].lower() != "penalty"]

            avg_shots = get_avg_shots_for_team(team_id, self.season)
            sample_size = max(1, int(random.gauss(avg_shots, 2)))
            sampled = random.sample(shots, min(sample_size, len(shots)))

            gk = get_goalkeeper_for_team(opponent_id, self.season)
            gk_modifier = 0.0
            if gk and gk["xgoals_gk_faced"] > 0:
                over = gk["goals_minus_xgoals_gk"]
                faced = gk["xgoals_gk_faced"]
                gk_modifier = -1.0 * (over / faced)

            for shot in sampled:
                base_prob = shot["shot_psxg"] if self.use_psxg else shot["shot_xg"]
                if base_prob is None:
                    continue

                if self.use_psxg:
                    adj_prob = base_prob
                else:
                    adj_prob = max(0.01, min(0.95, base_prob * (1.0 + gk_modifier)))

                if random.random() < adj_prob:
                    goals += 1
                    scorers.append(shot["shooter_player_id"])

        elif self.mode == "poisson":
            shots = get_shots_for_team(team_id, self.season)
            total_xg = sum(s["shot_xg"] for s in shots)
            total_games = len(set(s["game_id"] for s in shots))
            avg_xg_per_game = total_xg / total_games if total_games > 0 else 1.0

            gk = get_goalkeeper_for_team(opponent_id, self.season)
            gk_modifier = 0.0
            if gk and gk["xgoals_gk_faced"] > 0:
                over = gk["goals_minus_xgoals_gk"]
                faced = gk["xgoals_gk_faced"]
                gk_modifier = -1.0 * (over / faced)

            lam = max(0.1, avg_xg_per_game * (1.0 + gk_modifier))
            goals = np.random.poisson(lam)

        else:
            raise ValueError(f"Invalid mode: {self.mode}")

        return goals, scorers

    def run_simulations(self, n):
        self.n_simulations = n
        for _ in range(n):
            h_goals, a_goals = self.simulate_match()
            self.scorelines[(h_goals, a_goals)] += 1
            self.goal_totals["home"].append(h_goals)
            self.goal_totals["away"].append(a_goals)

            if h_goals > a_goals:
                self.outcomes["home_win"] += 1
            elif h_goals < a_goals:
                self.outcomes["away_win"] += 1
            else:
                self.outcomes["draw"] += 1

    def get_summary(self):
        return {
            "home_team_id": self.home_team_id,
            "away_team_id": self.away_team_id,
            "home_team_name": self.team_name_map.get(self.home_team_id, "Home"),
            "away_team_name": self.team_name_map.get(self.away_team_id, "Away"),
            "home_win_pct": self.outcomes["home_win"] / self.n_simulations,
            "away_win_pct": self.outcomes["away_win"] / self.n_simulations,
            "draw_pct": self.outcomes["draw"] / self.n_simulations,
            "avg_home_goals": sum(self.goal_totals["home"]) / self.n_simulations,
            "avg_away_goals": sum(self.goal_totals["away"]) / self.n_simulations
        }

    def get_scoreline_distribution(self):
        return {
            f"{h}-{a}": {
                "count": count,
                "pct": count / self.n_simulations
            }
            for (h, a), count in self.scorelines.items()
        }

    def get_top_scorers(self, side, limit=10):
        team_id = self.home_team_id if side == "home" else self.away_team_id
        scorers = self.scorer_totals[team_id].most_common(limit)
        return [
            {
                "player_id": pid,
                "player_name": self.player_name_map.get(pid, f"[{pid}]"),
                "goals": count
            }
            for pid, count in scorers
        ]

    def generate_analysis_paragraphs(self):
        summary = self.get_summary()
        home_name = summary["home_team_name"]
        away_name = summary["away_team_name"]

        lines = []

        # 1. Results
        lines.append(f"Over {self.n_simulations} simulated matches between {home_name} and {away_name}, "
                     f"{home_name} won {summary['home_win_pct']:.1%}, {away_name} won {summary['away_win_pct']:.1%}, "
                     f"and {summary['draw_pct']:.1%} ended in draws.")

        lines.append(f"Avg goals per match: {home_name} {summary['avg_home_goals']:.2f}, "
                     f"{away_name} {summary['avg_away_goals']:.2f}.")

        # 2. Shot quality
        home_xg = sum(s["shot_xg"] for s in get_shots_for_team(self.home_team_id, self.season))
        away_xg = sum(s["shot_xg"] for s in get_shots_for_team(self.away_team_id, self.season))
        lines.append(f"Season xG totals: {home_name} {home_xg:.1f}, {away_name} {away_xg:.1f}.")

        # 3. Defense via xGA
        home_xga = get_team_xga_per_game(self.home_team_id, self.season)
        away_xga = get_team_xga_per_game(self.away_team_id, self.season)
        lines.append(f"Season xGA per game: {home_name} {home_xga:.2f}, {away_name} {away_xga:.2f}.")

        # 4. Goalkeeper performance
        def gk_adj(gk): return gk["goals_minus_xgoals_gk"] / gk["xgoals_gk_faced"] if gk and gk["xgoals_gk_faced"] > 0 else 0
        home_gk = gk_adj(get_goalkeeper_for_team(self.home_team_id, self.season))
        away_gk = gk_adj(get_goalkeeper_for_team(self.away_team_id, self.season))

        if home_gk < -0.05:
            lines.append(f"{home_name}'s goalkeeper was a strength, exceeding expectations.")
        elif home_gk > 0.05:
            lines.append(f"{home_name}'s goalkeeper underperformed relative to xG faced.")

        if away_gk < -0.05:
            lines.append(f"{away_name}'s goalkeeper was notably strong.")
        elif away_gk > 0.05:
            lines.append(f"{away_name}'s keeper conceded more than expected.")

        # 5. Scorers
        top_home = self.get_top_scorers("home", 3)
        top_away = self.get_top_scorers("away", 3)
        if top_home:
            top_str = ", ".join(f"{p['player_name']} ({p['goals']})" for p in top_home)
            lines.append(f"Top scorers for {home_name}: {top_str}.")
        if top_away:
            top_str = ", ".join(f"{p['player_name']} ({p['goals']})" for p in top_away)
            lines.append(f"Top scorers for {away_name}: {top_str}.")

        # 6. Outliers
        if home_xg > away_xg and summary["home_win_pct"] < summary["away_win_pct"]:
            lines.append(f"Despite more xG, {home_name} won fewer simulations—perhaps due to poor finishing or defense.")
        elif away_xg > home_xg and summary["away_win_pct"] < summary["home_win_pct"]:
            lines.append(f"{home_name} won more despite lower xG—likely better execution.")

        # 7. Conclusion
        favored = home_name if summary["home_win_pct"] > summary["away_win_pct"] else away_name
        lines.append(f"In conclusion, {favored} appears to hold the edge based on simulation outcomes.")

        return "\n\n".join(lines)
