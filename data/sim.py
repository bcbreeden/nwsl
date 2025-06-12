import random
from collections import Counter, defaultdict
from data.db_game_shots import get_shots_for_team, get_avg_shots_for_team
from data.db_goalkeeper_xgoals import get_goalkeeper_for_team
from data.db_player_info import get_player_name_map
from data.db_team_info import get_team_name_map, get_team_abbreviation_map
from data.db_team_xgoals import (
    get_team_xga_per_game,
    get_league_avg_xga_per_game,
    get_team_shots_against_per_game,
    get_league_avg_shots_against_per_game
)

class MatchSimulator:
    def __init__(self, home_team_id, away_team_id, season, home_advantage, away_advantage, mode="shot", exclude_penalties=True, use_psxg=False, excluded_player_ids=None):
        """
        Initializes the MatchSimulator with preloaded shot-level data and modifiers for simulation.

        Args:
            home_team_id (str): ID of the home team.
            away_team_id (str): ID of the away team.
            season (int): Season year to pull data from.
            home_advantage (float): Modifier applied to the home team's shot volume (e.g., 1.05 = +5%).
            away_advantage (float): Modifier applied to the away team's shot volume.
            mode (str, optional): Currently unused but reserved for future xG simulation types. Defaults to "shot".
            exclude_penalties (bool, optional): Whether to exclude penalty shots from simulation. Defaults to True.
            use_psxg (bool, optional): Whether to use post-shot xG (PSxG) instead of xG. Defaults to False.
            excluded_player_ids (list[str], optional): List of player IDs to exclude from all simulations. Defaults to None.

        Attributes:
            cached_team_shots (dict): All shot events for each team, filtered for penalties if specified.
            filtered_team_shots (dict): Shots filtered to exclude any taken by excluded players.
            cached_avg_shots (dict): Average number of shots per game per team.
            cached_goalkeepers (dict): Goalkeeper over/under-performance data.
            cached_avg_xg_per_game (dict): Team-level average xG per game, used for context and normalization.
            cached_xga_per_game (dict): Opponent defensive strength based on expected goals allowed (xGA).
            player_name_map (dict): Maps player IDs to human-readable names.
            team_name_map (dict): Maps team IDs to human-readable names.
            team_abbreviation_map (dict): Maps team IDs to short display abbreviations.
            home_advantage (float): Shot volume modifier for home team.
            away_advantage (float): Shot volume modifier for away team.
            n_simulations (int): Number of simulations run.
            scorelines (Counter): Tracks scoreline outcomes (e.g., (1, 0): 87).
            outcomes (Counter): Tracks win/draw/loss frequencies.
            goal_totals (defaultdict): Tracks total goals scored by each side across simulations.
            scorer_totals (defaultdict): Tracks goals scored per player across simulations.
        """
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
        self.filtered_team_shots = {}
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
        self.league_avg_xga = get_league_avg_xga_per_game(season)
        self.league_avg_sapg = get_league_avg_shots_against_per_game(season)

        # Shots Against Per Game for each team in the current match.
        self.cached_sapg_per_game = {
            team_id: get_team_shots_against_per_game(team_id, season)
            for team_id in [self.home_team_id, self.away_team_id]
        }

        # Shot filtering logic
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
        """
        Simulates a single match between the selected home and away teams.

        This function performs the following:
            1. Calls `simulate_team_goals` for both the home and away teams.
            2. Tracks which players scored in the match.
            3. Updates internal scorer tally for each team.
            4. Returns the simulated final scoreline.

        The results from this method are used by `run_simulations()` to build
        aggregate statistics like scoreline distributions, win/draw/loss rates,
        and top scorers.

        Returns:
            tuple:
                home_goals (int): The number of goals scored by the home team.
                away_goals (int): The number of goals scored by the away team.

        Example:
            >>> sim = MatchSimulator(...)
            >>> sim.simulate_match()
            (2, 1)

            This means the home team scored 2 and the away team scored 1 in this sim.
        """
        home_goals, home_scorers = self.simulate_team_goals(self.home_team_id, self.away_team_id)
        away_goals, away_scorers = self.simulate_team_goals(self.away_team_id, self.home_team_id)

        for pid in home_scorers:
            self.scorer_totals[self.home_team_id][pid] += 1
        for pid in away_scorers:
            self.scorer_totals[self.away_team_id][pid] += 1

        return home_goals, away_goals

    def simulate_team_goals(self, team_id, opponent_id):
        """
        Simulates the number of goals scored by a team against a given opponent,
        based on historical shot data, defensive adjustments, and goalkeeper performance.

        This method performs the following steps:
            1. Filters eligible shots for the team (already pre-filtered by exclusions).
            2. Adjusts the average number of shots to take based on the opponent's defensive quality (xGA) and shot volume allowed (shots against).
            3. Applies home/away advantage to modify shot volume.
            4. Randomly samples a number of shots based on the adjusted average.
            5. For each sampled shot:
                - Uses PSxG or xG depending on configuration.
                - Applies a goalkeeper modifier (if using xG) to reflect shot-stopping performance.
                - Runs a Bernoulli trial using the adjusted probability to determine whether the shot results in a goal.
            6. Returns the total number of goals and a list of player IDs who scored in this simulation.

        Args:
            team_id (str): The ID of the attacking team.
            opponent_id (str): The ID of the defending team.

        Returns:
            tuple:
                goals (int): The number of goals scored in this simulation.
                scorers (list[str]): List of player IDs who scored goals in this simulation.

        Example:
            If the team takes 12 adjusted shots, and 3 have goal probabilities above 0.4,
            the Bernoulli trials might result in 2 goals being scored. Those 2 player IDs
            are returned as the scorers.
        """
        scorers = []
        goals = 0

        shots = self.filtered_team_shots[team_id]
        avg_shots = self.cached_avg_shots[team_id]

        adjusted_avg_shots = self.get_adjusted_avg_shots(avg_shots, opponent_id)
        sampled = self.get_sampled_shots(team_id, shots, adjusted_avg_shots)
        gk_modifier = self.get_goalkeeper_modifier(opponent_id)

        # Simulate shot outcomes
        for shot in sampled:
            base_prob = shot["shot_psxg"] if self.use_psxg else shot["shot_xg"]
            if base_prob is None:
                continue

            if self.use_psxg:
                adj_prob = base_prob  # PSxG already includes goalkeeper effect
            else:
                adj_prob = max(0.01, min(0.95, base_prob * (1.0 + gk_modifier)))

            if random.random() < adj_prob:
                goals += 1
                scorers.append(shot["shooter_player_id"])

        return goals, scorers


    def run_simulations(self, n):
        """
        Runs N full-match simulations between the selected home and away teams.

        This method:
            1. Repeatedly calls `simulate_match()` N times.
            2. Records the resulting scoreline (e.g., 2–1) in a frequency counter.
            3. Tracks goal totals per team across all simulations.
            4. Aggregates match outcomes as home wins, away wins, or draws.
            5. Updates internal state used by other summary/reporting functions.

        Args:
            n (int): Number of match simulations to run.

        Side Effects:
            - Updates `self.n_simulations` to reflect the count.
            - Populates or updates:
                - `self.scorelines`: Counter of (home_goals, away_goals)
                - `self.goal_totals`: Dict of all home and away goal values
                - `self.outcomes`: Counter of win/draw categories
                - `self.scorer_totals`: (via `simulate_match()`)

        Example:
            >>> sim = MatchSimulator(...)
            >>> sim.run_simulations(1000)
            >>> sim.scorelines[(1, 0)]  # Number of 1–0 results
            243
        """
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
        """
        Returns a high-level summary of simulation results, including team identifiers,
        win percentages, and average goals scored.

        This method should be called after `run_simulations()` has been executed.

        Returns:
            dict: A dictionary containing:
                - home_team_id (str): The ID of the home team.
                - away_team_id (str): The ID of the away team.
                - home_team_name (str): Full name of the home team.
                - away_team_name (str): Full name of the away team.
                - home_team_abbreviation (str): Short name/abbreviation of the home team.
                - away_team_abbreviation (str): Short name/abbreviation of the away team.
                - home_win_pct (float): Proportion of simulations won by the home team.
                - away_win_pct (float): Proportion of simulations won by the away team.
                - draw_pct (float): Proportion of simulations that ended in a draw.
                - avg_home_goals (float): Average number of goals scored by the home team.
                - avg_away_goals (float): Average number of goals scored by the away team.

        Example:
            >>> sim.run_simulations(1000)
            >>> summary = sim.get_summary()
            >>> summary["home_win_pct"]
            0.41
        """
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
        """
        Returns a list of scoreline outcomes sorted by frequency, based on all simulations run.

        Each entry includes the raw goal counts, frequency, and percentage of total simulations.

        Returns:
            list[dict]: List of dictionaries, each containing:
                - scoreline (str): Formatted as "X-Y" (home-away goals).
                - home_goals (int): Number of goals scored by the home team.
                - away_goals (int): Number of goals scored by the away team.
                - count (int): How many times this scoreline occurred.
                - pct (float): Frequency as a percentage of total simulations.

        Example:
            >>> sim.run_simulations(1000)
            >>> sim.get_scoreline_distribution()[0]
            {
                "scoreline": "1-0",
                "home_goals": 1,
                "away_goals": 0,
                "count": 187,
                "pct": 0.187
            }
        """
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
        """
        Returns the top scorers for either the home or away team across all simulations.

        Args:
            side (str): Either "home" or "away" — determines which team's scorers to return.
            limit (int, optional): Maximum number of top scorers to return. Defaults to 10.

        Returns:
            list[dict]: List of top scorer dictionaries, each containing:
                - player_id (str): The player’s ID.
                - player_name (str): Human-readable name of the player (from lookup).
                - goals (int): Number of goals scored by this player in all simulations.

        Example:
            >>> sim.get_top_scorers("home", limit=3)
            [
                {"player_id": "player123", "player_name": "Debinha", "goals": 14},
                {"player_id": "player456", "player_name": "Kerolin", "goals": 11},
                ...
            ]
        """
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

    def get_adjusted_avg_shots(self, avg_shots, opponent_id):
        """
        Calculates the average number of shots to simulate for a team
        based on opponent defensive quality (xGA) and volume (shots against).

        This blends two modifiers:
            - xGA Modifier: How much xG the opponent typically concedes vs league average
            - SAPG Modifier: How many shots the opponent concedes vs league average

        The final defense modifier is the average of those two values.

        Args:
            avg_shots (float): The team’s base average shots per game.
            opponent_id (str): The opposing team’s ID.

        Returns:
            float: Adjusted average shots per game after applying defense modifiers.

        Example:
            If a team averages 12.0 shots/game, and:
                opponent_xga = 1.6, league_avg_xga = 1.2 → xga_mod = 1.33
                opponent_sapg = 14.0, league_avg_sapg = 10.0 → sapg_mod = 1.40
                defense_modifier = (1.33 + 1.40) / 2 = 1.365

            Then:
                adjusted_avg_shots = 12.0 * 1.365 = 16.38
        """
        opponent_xga = self.cached_xga_per_game.get(opponent_id)
        opponent_sapg = self.cached_sapg_per_game.get(opponent_id)

        xga_mod = opponent_xga / self.league_avg_xga if opponent_xga and self.league_avg_xga else 1.0
        sapg_mod = opponent_sapg / self.league_avg_sapg if opponent_sapg and self.league_avg_sapg else 1.0

        defense_modifier = (xga_mod + sapg_mod) / 2
        return avg_shots * defense_modifier

    def get_sampled_shots(self, team_id, shots, adjusted_avg_shots):
        """
        Returns a list of randomly sampled shots for a team, accounting for
        home/away advantage and injecting Gaussian randomness.

        Args:
            team_id (str): The team ID.
            shots (list[dict]): List of eligible shots for this simulation.
            adjusted_avg_shots (float): Adjusted shot volume based on defensive modifiers.

        Returns:
            list[dict]: Sampled shot dictionaries for this simulation.

        Example:
            If adjusted_avg_shots = 14.0 and home_advantage = 1.05, then
            sample_mean = 14.7 and actual sampled count might vary around that
        """
        advantage = self.home_advantage if team_id == self.home_team_id else self.away_advantage
        sample_mean = adjusted_avg_shots * advantage
        sample_size = max(1, int(random.gauss(sample_mean, 2)))
        return random.sample(shots, min(sample_size, len(shots)))

    def get_goalkeeper_modifier(self, opponent_id):
        """
        Calculates a goalkeeper performance modifier based on how much
        they over- or under-perform expected goals faced.

        A positive modifier reduces the shooter's scoring chance,
        while a negative modifier increases it.

        Args:
            opponent_id (str): The opposing team’s ID (to retrieve their GK stats).

        Returns:
            float: A modifier to apply to xG (e.g., +0.05 for strong GK, -0.08 for weak).
                Will return 0.0 if no data is available.
        
        Example:
            goals_minus_xgoals_gk = -2.0 (overperformed)
            xgoals_gk_faced = 20.0
            → modifier = -1.0 * (-2.0 / 20.0) = 0.10
            → scoring chance is reduced by 10%
        """
        gk = self.cached_goalkeepers.get(opponent_id)
        if gk and gk["xgoals_gk_faced"] > 0:
            over = gk["goals_minus_xgoals_gk"]
            faced = gk["xgoals_gk_faced"]
            return -1.0 * (over / faced)
        return 0.0