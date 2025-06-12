import random
from collections import Counter, defaultdict

from data.db_game_shots import get_shots_for_team, get_avg_shots_for_team
from data.db_goalkeeper_xgoals import get_goalkeeper_for_team
from data.db_player_info import get_player_name_map
from data.db_team_info import get_team_name_map, get_team_abbreviation_map
from data.db_team_xgoals import get_team_xga_per_game, get_league_avg_xga_per_game


class MatchSimulator:
    def __init__(self, home_team_id, away_team_id, season, home_advantage, away_advantage, mode="shot", exclude_penalties=True, use_psxg=False, excluded_player_ids=None):
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id
        self.season = season
        self.mode = mode.lower()
        self.exclude_penalties = exclude_penalties
        self.n_simulations = 0
        self.use_psxg = use_psxg
        self.cached_team_shots = {}
        self.cached_avg_shots = {}
        self.cached_goalkeepers = {}
        self.cached_avg_xg_per_game = {}
        self.filtered_team_shots = {} # Will hold the shots with all filters and exclusions applied.
        self.cached_xga_per_game = {
            team_id: get_team_xga_per_game(team_id, self.season)
            for team_id in [self.home_team_id, self.away_team_id]
        }

        self.player_name_map = get_player_name_map()
        self.team_name_map = get_team_name_map()
        self.team_abbreviation_map = get_team_abbreviation_map()

        self.scorelines = Counter()
        self.outcomes = Counter()
        self.goal_totals = defaultdict(list)
        self.scorer_totals = defaultdict(Counter)

        self.home_advantage = home_advantage
        self.away_advantage = away_advantage

        self.excluded_player_ids = set(excluded_player_ids or [])

        for team_id in [self.home_team_id, self.away_team_id]:
            # Get all shots
            all_shots = get_shots_for_team(team_id, self.season)

            # Optionally filter penalties
            if self.exclude_penalties:
                all_shots = [
                    s for s in all_shots
                    if s["pattern_of_play"] and s["pattern_of_play"].lower() != "penalty"
                ]
            
            # Cache unfiltered shots
            self.cached_team_shots[team_id] = all_shots

            # Cache average shots per game
            self.cached_avg_shots[team_id] = get_avg_shots_for_team(team_id, self.season)

            # Cache goalkeeper stats
            self.cached_goalkeepers[team_id] = get_goalkeeper_for_team(team_id, self.season)

            # Cache filtered shots (exclude players)
            self.filtered_team_shots[team_id] = [
                s for s in all_shots
                if s["shooter_player_id"] not in self.excluded_player_ids
            ]

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

        shots = self.filtered_team_shots[team_id]

        avg_shots = self.cached_avg_shots[team_id]

        # Incorporate opponent defensive strength using xGA
        opponent_xga = self.cached_xga_per_game.get(opponent_id, 1.5)  # default to league avg if missing
        league_avg_xga = get_league_avg_xga_per_game(self.season)
        defense_modifier = opponent_xga / league_avg_xga
        adjusted_avg_shots = avg_shots * defense_modifier

        advantage = self.home_advantage if team_id == self.home_team_id else self.away_advantage
        sample_size = max(1, int(random.gauss(adjusted_avg_shots * advantage, 2)))
        sampled = random.sample(shots, min(sample_size, len(shots)))

        # Goalkeeper adjustment
        gk = self.cached_goalkeepers.get(opponent_id)
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
                adj_prob = base_prob  # PSxG already accounts for goalkeeper
            else:
                adj_prob = max(0.01, min(0.95, base_prob * (1.0 + gk_modifier)))

            if random.random() < adj_prob:
                goals += 1
                scorers.append(shot["shooter_player_id"])

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
            "home_team_abbreviation": self.team_abbreviation_map.get(self.home_team_id, "Home"),
            "away_team_abbreviation": self.team_abbreviation_map.get(self.away_team_id, "Away"),
            "home_win_pct": self.outcomes["home_win"] / self.n_simulations,
            "away_win_pct": self.outcomes["away_win"] / self.n_simulations,
            "draw_pct": self.outcomes["draw"] / self.n_simulations,
            "avg_home_goals": sum(self.goal_totals["home"]) / self.n_simulations,
            "avg_away_goals": sum(self.goal_totals["away"]) / self.n_simulations
        }

    def get_scoreline_distribution(self):
        sorted_scorelines = sorted(
            self.scorelines.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [
            {
                "scoreline": f"{h}-{a}",
                "home_goals": h,
                "away_goals": a,
                "count": count,
                "pct": count / self.n_simulations
            }
            for (h, a), count in sorted_scorelines
        ]

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
