from flask import Flask, render_template, request, redirect, url_for, abort, session, make_response
from data import (db_games_xgoals, db_games, db_goalkeeper_goals_added,db_goalkeeper_xgoals,
                db_player_goals_added, db_player_info, db_player_xgoals, db_player_xpass,
                db_team_goals_added, db_team_info, db_team_xgoals, db_team_xpass, db_game_flow,
                db_stadium_info, db_team_strength, db_team_xgoals_boundaries, db_team_xpass_boundaries,
                db_team_goals_added_boundaries, db_game_shots, db_game_goals, sim, data_util)
from plots import (plot_deviation_from_average_chart, plot_team_strength_donut, get_donut_plot_for_team_results, get_donut_plot_for_goals,
                get_donut_plot_for_pass_completion, plot_bar_chart, generate_shot_marker_plot)
from momentum_plot import generate_momentum_plot
from datetime import datetime
from collections import defaultdict
from blog_loader import load_blog_posts, get_post_by_slug
import markdown
import random
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = os.environ.get('KEY')

SEASONS = data_util.ALL_SEASONS

def nocache(view):
    """Decorator to set headers that disable caching."""
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    # Maintain Flask route metadata
    no_cache.__name__ = view.__name__
    return no_cache

'''
Renders the index template.
'''
@app.route('/', methods=['GET', 'POST'])
@nocache
def index():
    if request.method == 'POST':
        new_season = request.form.get('season_year')
        if new_season:
            session['season'] = int(new_season)
            return redirect(url_for('index'))
    selected_season = get_selected_season()
    teams_data = db_team_xgoals.get_top_team_xgoals_stat(selected_season, 'points')
    top_5_goalscorers = db_player_xgoals.get_top_player_xgoals_stat(selected_season, 'goals', 5)
    top_5_assists = db_player_xgoals.get_top_player_xgoals_stat(selected_season, 'primary_assists', 5)
    shots_on_target = db_player_xgoals.get_player_xgoals_minimum_shots(selected_season, 'shots_on_target_perc', 5, 10)
    total_shots = db_player_xgoals.get_top_player_xgoals_stat(selected_season, 'shots', 5)
    minutes_played_df = db_player_xgoals.get_defender_minutes_played(selected_season, 'minutes_played', 5)
    minutes_played_non_df = db_player_xgoals.get_minutes_played_non_df(selected_season, 'minutes_played', 5)
    return render_template('index.html',
                           teams_data = teams_data,
                           top_scorers = top_5_goalscorers,
                           top_assists = top_5_assists,
                           shots_on_target = shots_on_target,
                           minutes_played_df = minutes_played_df,
                           minutes_played_non_df = minutes_played_non_df,
                           total_shots = total_shots,
                           season = selected_season,
                           seasons = SEASONS)

@app.route('/league')
@nocache
def league():
    selected_season = get_selected_season()
    top_5_goalscorers = db_player_xgoals.get_top_player_xgoals_stat(selected_season, 'goals', 5)
    top_5_assists = db_player_xgoals.get_top_player_xgoals_stat(selected_season, 'primary_assists', 5)
    shots_on_target = db_player_xgoals.get_player_xgoals_minimum_shots(selected_season, 'shots_on_target_perc', 5, 10)
    total_shots = db_player_xgoals.get_top_player_xgoals_stat(selected_season, 'shots', 5)
    minutes_played_df = db_player_xgoals.get_defender_minutes_played(selected_season, 'minutes_played', 5)
    minutes_played_non_df = db_player_xgoals.get_minutes_played_non_df(selected_season, 'minutes_played', 5)
    return render_template('league.html',
                            top_scorers = top_5_goalscorers,
                            top_assists = top_5_assists,
                            shots_on_target = shots_on_target,
                            minutes_played_df = minutes_played_df,
                            minutes_played_non_df = minutes_played_non_df,
                            total_shots = total_shots,
                            season = selected_season,
                            seasons = SEASONS)

@app.route('/teams')
@nocache
def teams():
    selected_season = get_selected_season()
    team_data = db_team_xgoals.get_top_team_xgoals_stat(selected_season, 'team_strength')
    team_strength_history = db_team_xgoals.get_team_strength_by_season(selected_season)
    return render_template('teams.html',
                           teams = team_data,
                           team_strength_history = team_strength_history,
                           season = selected_season,
                           seasons = SEASONS)

@app.route('/team', methods=['GET', 'POST'])
@nocache
def team():
    selected_season = get_selected_season()
    if request.method == 'POST':
        team_id = request.form.get('team_id')
        obj_id = request.form.get('obj_id')
        team_xgoals_data = db_team_xgoals.get_team_xgoals_by_season(team_id, selected_season)
        team_xpass_data = db_team_xpass.get_team_xpass_by_season(team_id, selected_season)
        team_goals_added_data = db_team_goals_added.get_team_goals_added_by_season(team_id, selected_season)
        team_strength_data = db_team_strength.get_team_strength(team_id, selected_season)
        team_xgoal_boundary_data = db_team_xgoals_boundaries.get_team_xgoal_boundaries_by_season(selected_season)
        team_xpass_boundary_data = db_team_xpass_boundaries.get_team_xpass_boundaries_by_season(selected_season)
        team_goals_added_boundaries = db_team_goals_added_boundaries.get_team_goals_add_boundaries_by_season(selected_season)

        team_goalkeepers = db_goalkeeper_xgoals.get_goalkeepers_for_team(team_id, selected_season, limit=3)
        team_players = db_player_xgoals.get_all_player_xgoal_by_team(team_id, selected_season)

        team_strength = team_xgoals_data['team_strength']
        strength_fig_json, strength_config = plot_team_strength_donut(team_strength)

        team_record = db_games.get_team_record_by_season(team_id, selected_season)
        game_results = db_games.get_team_game_results(team_id, selected_season)
        for row in game_results:
            print(dict(row))


        five_recent_games = game_results[:5][::-1]

        stadium = db_stadium_info.get_stadium_by_id(db_games.get_most_recent_home_stadium_id(team_id, selected_season))

        strength_stats_to_plot = [
                                "xgoal_difference",
                                "goal_difference",
                                "xpoints",
                                "points",
                                "goal_diff_minus_xgoal_diff",
                                "goalfor_xgoalfor_diff",
                                "psxg_xg_diff"
                            ]
        strength_bar_json, strength_bar_config = plot_bar_chart(strength_stats_to_plot, team_strength_data)

        results_fig_json, results_config = get_donut_plot_for_team_results(
                                                                        team_record['wins'],
                                                                        team_record['losses'],
                                                                        team_record['draws'],
                                                                        team_xgoals_data['points']
                                                                        )
        goals_fig_json, goals_config = get_donut_plot_for_goals(team_xgoals_data['goals_for'], team_xgoals_data['goals_against'])
        pass_fig_json, pass_config = get_donut_plot_for_pass_completion(team_xpass_data['pass_completion_percentage_for'])



        return render_template('team.html',
                                team_xgoals_data = team_xgoals_data,
                                season = selected_season,
                                seasons = SEASONS,
                                strength_fig_json = strength_fig_json, 
                                strength_config = strength_config,
                                team_record = team_record,
                                game_results = game_results,
                                five_recent_games = five_recent_games,
                                stadium = stadium,
                                results_fig_json = results_fig_json,
                                results_config = results_config,
                                goals_fig_json = goals_fig_json,
                                goals_config = goals_config,
                                pass_fig_json = pass_fig_json,
                                pass_config = pass_config,
                                strength_bar_json = strength_bar_json,
                                strength_bar_config = strength_bar_config,
                                team_xpass_data = team_xpass_data,
                                team_goals_added_data = team_goals_added_data,
                                team_xgoal_boundary_data = team_xgoal_boundary_data,
                                team_xpass_boundary_data = team_xpass_boundary_data,
                                team_goals_added_boundaries = team_goals_added_boundaries,
                                team_goalkeepers = team_goalkeepers,
                                team_players=team_players)
    if request.method == 'GET':
        redirect(url_for('teams'))


@app.route('/team_comparison', methods=['GET', 'POST'])
@nocache
def team_comparison():
    selected_season = get_selected_season()
    team_data = db_team_xgoals.get_top_team_xgoals_stat(selected_season, 'points')
    team1_id = request.form.get('team1')
    team2_id = request.form.get('team2')
    team1_data = db_team_xgoals.get_team_xgoals_by_season(team1_id, selected_season)
    team2_data = db_team_xgoals.get_team_xgoals_by_season(team2_id, selected_season)
    ordered_stats = [
        {'name': 'count_games', 'label': 'Matches Played', 'type': 'neutral'},
        {'name': 'team_strength', 'label': 'Team Strength', 'type': 'positive'},
        {'name': 'shots_for', 'label': 'Shots For', 'type': 'positive'},
        {'name': 'shots_against', 'label': 'Shots Against', 'type': 'negative'},
        {'name': 'goals_for', 'label': 'Goals For', 'type': 'positive'},
        {'name': 'goals_against', 'label': 'Goals Against', 'type': 'negative'},
        {'name': 'goal_difference', 'label': 'Goal Differential', 'type': 'positive'},
        {'name': 'xgoals_for', 'label': 'xGoals For', 'type': 'positive'},
        {'name': 'psxg', 'label': 'Post Shot xG', 'type': 'positive'},
        {'name': 'psxg_xg_diff', 'label': 'PSxG Diff', 'type': 'positive'},
        {'name': 'xgoals_against', 'label': 'xGoals Against', 'type': 'negative'},
        {'name': 'xgoal_difference', 'label': 'xGoals Differential', 'type': 'positive'},
        {'name': 'goal_difference_minus_xgoal_difference', 'label': 'Goal Diff - xGoal Diff', 'type': 'neutral'},
        {'name': 'points', 'label': 'Points', 'type': 'positive'},
        {'name': 'xpoints', 'label': 'xPoints', 'type': 'positive'},
        {'name': 'goalfor_xgoalfor_diff', 'label': 'Goal For | xGoal For Diff', 'type': 'positive'}
    ]

    return render_template('team_comparison.html',
                            team1_data = team1_data,
                            team2_data = team2_data,
                            ordered_stats = ordered_stats,
                            teams = team_data,
                            season = selected_season,
                            seasons = SEASONS)

@app.route('/games')
@nocache
def games():
    selected_season = get_selected_season()
    games_data = db_games.get_all_games_by_season(selected_season)
    games_xgoals_data = db_games_xgoals.get_all_games_xgoals_by_season(selected_season)
    return render_template('games.html',
                           games_data = games_data,
                           games_xgoals_data = games_xgoals_data,
                           season = selected_season,
                           seasons = SEASONS)

@app.route('/game', methods=['GET', 'POST'])
@nocache
def game():
    selected_season = get_selected_season()
    if request.method == 'POST':
        # GAME DATA
        game_data = db_games.get_game_by_id(request.form.get('game_id'))
        away_team_id = game_data['away_team_id']
        away_team_abbr = game_data['away_team_abbreviation']
        home_team_id = game_data['home_team_id']
        home_team_abbr = game_data['home_team_abbreviation']

        # PLAYER INFO DATA
        player_info = db_player_info.get_all_players_info()
        player_info_data = {row['player_id']: row['player_name'] for row in player_info}

        # TEAM INFO DATA
        team_info = db_team_info.get_all_teams_info()
        team_info_data = {row['team_id']: row['team_abbreviation'] for row in team_info}

        # SHOT DATA
        all_shots_data = db_game_shots.get_shots_by_game_id(request.form.get('game_id'))
        all_shot_data_with_markers = _insert_event_markers(all_shots_data, home_team_id, away_team_id)
        home_shots_data = [shot for shot in all_shots_data if shot['team_id'] == home_team_id]
        away_shots_data = [shot for shot in all_shots_data if shot['team_id'] == away_team_id]
        home_shot_map_json, home_shot_map_config = generate_shot_marker_plot(request.form.get('game_id'), game_data, player_info, home_shots_data, home_team_abbr)
        away_shot_map_json, away_shot_map_config = generate_shot_marker_plot(request.form.get('game_id'), game_data, player_info, away_shots_data, away_team_abbr)
        goal_data = db_game_goals.get_goals_by_game_id(request.form.get('game_id'))
        team_psxgs = db_game_shots.get_total_psxg_by_game_id(request.form.get('game_id'))
        team_total_shots = db_game_shots.get_total_shots_by_game_id(request.form.get('game_id'))
        team_shots_on_target = db_game_shots.get_total_shots_on_target_by_game_id(request.form.get('game_id'))

        # GAME FLOW DATA
        game_flow_data = db_game_flow.get_game_flow_by_game_id(request.form.get('game_id'))
        game_flow_json, game_flow_config = generate_momentum_plot(request.form.get('game_id'))
        
        # XGOALS DATA
        game_xgoals_data = db_games_xgoals.get_game_xgoals_by_id(request.form.get('game_id'))

        return render_template('game.html',
                                game_data = game_data,
                                game_xgoals_data = game_xgoals_data,
                                game_flow_data = game_flow_data,
                                game_flow_json = game_flow_json, 
                                game_flow_config = game_flow_config,
                                season = selected_season,
                                seasons = SEASONS,
                                shot_data = all_shot_data_with_markers,
                                player_info_data=player_info_data,
                                team_info_data = team_info_data,
                                goal_data = goal_data,
                                team_psxgs = team_psxgs,
                                team_total_shots = team_total_shots,
                                team_shots_on_target = team_shots_on_target,
                                home_shot_map_json = home_shot_map_json,
                                home_shot_map_config = home_shot_map_config,
                                away_shot_map_json = away_shot_map_json,
                                away_shot_map_config = away_shot_map_config)
    else:
        return redirect(url_for('games'))

@app.route('/players')
@nocache
def players():
    selected_season = get_selected_season()
    players_xgoals_data = db_player_xgoals.get_top_player_xgoals_stat(selected_season)
    players_xpass_data = db_player_xpass.get_all_player_xpass(selected_season)

    combined_data = zip(players_xgoals_data, players_xpass_data)
    return render_template('players.html',
                           player_data = combined_data,
                           season = selected_season,
                           seasons = SEASONS)

@app.route('/player', methods=['GET', 'POST'])
@nocache
def player():
    selected_season = get_selected_season()
    if request.method == 'POST':
        x_goals_stats_to_plot = [
        'shots', 'shots_on_target', 'shots_on_target_perc', 'xgoals_xassists_per_90',
        'goals', 'xgoals', 'xassists', 'xplace', 'key_passes', 'primary_assists', 'xgoals_plus_xassists',
        'points_added', 'xpoints_added'
        ]
        x_pass_stats_to_plot = [
        'attempted_passes', 'pass_completion_percentage', 'passes_completed_over_expected',
        'xpass_completion_percentage', 'avg_vertical_distance_yds', 'avg_distance_yds',
        'passes_completed_over_expected_p100', 'share_team_touches'
        ]

        defense_to_plot = {
            'interrupting_goals_added_raw', 'interrupting_goals_added_above_avg',
            'interrupting_count_actions', 'fouling_goals_added_raw',
            'fouling_goals_added_above_avg', 'fouling_count_actions',
            'receiving_goals_added_raw', 'receiving_goals_added_above_avg',
            'receiving_count_actions'
        }
        player_id = request.form.get('player_id')
        obj_id = request.form.get('obj_id')
        
        player_xgoals_data = db_player_xgoals.get_player_xgoal_data(player_id, selected_season)
        player_xpass_data = db_player_xpass.get_player_xpass(player_id, selected_season)
        player_goals_added_data = db_player_goals_added.get_player_goals_added_by_season(player_id, selected_season)
        player_xgoals_all_seasons_data = db_player_xgoals.get_player_xgoal_data_all_seasons(player_id)

        xgoals_fig_json, xgoals_config = plot_deviation_from_average_chart(x_goals_stats_to_plot, player_xgoals_data)
        xpass_fig_json, xpass_config = plot_deviation_from_average_chart(x_pass_stats_to_plot, player_xpass_data)
        defense_fig_json, defense_config = plot_deviation_from_average_chart(defense_to_plot, player_goals_added_data)
        
        return render_template('player.html',
                               player_id = player_id,
                               obj_id = obj_id,
                               player_xgoals_data = player_xgoals_data,
                               player_xpass_data = player_xpass_data,
                               player_goals_added_data = player_goals_added_data,
                               xgoals_fig_json = xgoals_fig_json,
                               xgoals_config = xgoals_config,
                               xpass_fig_json = xpass_fig_json,
                               xpass_config = xpass_config,
                               defense_fig_json = defense_fig_json,
                               defense_config = defense_config,
                               season = selected_season,
                               seasons = SEASONS,
                               player_season_data = player_xgoals_all_seasons_data)
    return redirect(url_for('players'))

@app.route('/goalkeepers', methods=['GET', 'POST'])
@nocache
def goalkeepers():
    selected_season = get_selected_season()
    goalkeeper_data = db_goalkeeper_xgoals.get_all_goalkeepers_xgoals_by_season(selected_season)
    return render_template('goalkeepers.html',
                           keeper_data = goalkeeper_data,
                           season = selected_season,
                           seasons = SEASONS)

@app.route('/goalkeeper', methods=['GET', 'POST'])
@nocache
def goalkeeper():
    selected_season = get_selected_season()
    if request.method == 'POST':
        player_id = request.form.get('player_id')
        obj_id = request.form.get('obj_id')
        keeper_xgoal_data = db_goalkeeper_xgoals.get_goalkeeper_xgoals_by_season(player_id=player_id, season=selected_season)
        keeper_goals_added_data = db_goalkeeper_goals_added.get_goalkeeper_goals_added_by_season(player_id=player_id, season=selected_season)
        for key in keeper_xgoal_data.keys():
            print(f"{key}: {keeper_xgoal_data[key]}")
        
        xgoals_stats_to_plot = ['shots_faced',
                                'goals_conceded',
                                'saves',
                                'share_headed_shots',
                                'xgoals_gk_faced',
                                'goals_minus_xgoals_gk',
                                'goals_divided_by_xgoals_gk',
                                'save_perc'
                                ]

        goals_added_stats_to_plot = ['claiming_goals_added_raw',
            'claiming_goals_added_above_avg',
            'claiming_count_actions',
            'fielding_goals_added_raw',
            'fielding_goals_added_above_avg',
            'fielding_count_actions',
            'handling_goals_added_raw',
            'handling_goals_added_above_avg',
            'handling_count_actions',
            'passing_goals_added_raw',
            'passing_goals_added_above_avg',
            'passing_count_actions',
            'shotstopping_goals_added_raw',
            'shotstopping_goals_added_above_avg',
            'shotstopping_count_actions',
            'sweeping_goals_added_raw',
            'sweeping_goals_added_above_avg',
            'sweeping_count_actions'
            ]

        keeper_fig_json_xgoals, keeper_config_xgoals = plot_deviation_from_average_chart(xgoals_stats_to_plot, keeper_xgoal_data)
        keeper_fig_json_goals_added, keeper_config_goals_added = plot_deviation_from_average_chart(goals_added_stats_to_plot, keeper_goals_added_data)
        

        return render_template('goalkeeper.html',
                                player_id = player_id,
                                obj_id = obj_id,
                                keeper_xgoal_data  = keeper_xgoal_data,
                                keeper_goals_added_data = keeper_goals_added_data,
                                keeper_fig_json_xgoals = keeper_fig_json_xgoals,
                                keeper_config_xgoals = keeper_config_xgoals,
                                keeper_fig_json_goals_added = keeper_fig_json_goals_added,
                                keeper_config_goals_added = keeper_config_goals_added,
                                season = selected_season,
                                seasons = SEASONS)
    
    goalkeeper_data = db_goalkeeper_xgoals.get_all_goalkeepers_xgoals_by_season(selected_season)
    return render_template('goalkeepers.html',
                           keeper_data = goalkeeper_data,
                           season = selected_season,
                           seasons = SEASONS)

@app.route('/simulations')
@nocache
def simulations():
    selected_season = get_selected_season()
    team_data = db_team_xgoals.get_top_team_xgoals_stat(selected_season, 'points')
    teams_dict = [dict(team) for team in team_data]

    players_data = db_player_xgoals.get_top_player_xgoals_stat(season=selected_season)
    players_by_team = defaultdict(list)
    for player in players_data:
        players_by_team[player['team_id']].append(dict(player))  # Convert sqlite3.Row → dict

    return render_template('simulations.html',
                           season=selected_season,
                           seasons=SEASONS,
                           teams=team_data,
                           teams_dict = teams_dict,
                           players_by_team=dict(players_by_team))


@app.route('/simulation_results', methods=['GET', 'POST'])
@nocache
def simulation_results():
    selected_season = get_selected_season()
    home_team_id = request.form.get("home_team")
    away_team_id = request.form.get("away_team")           
    n_simulations = int(request.form.get("num_sims", 0))
    use_psxg = "psxg" in request.form
    include_penalties = "pks" in request.form
    home_advantage = float(request.form.get("home_advantage", 1.05))
    away_advantage = float(request.form.get("away_advantage", 0.95))
    excluded_player_ids = set(request.form.getlist("exclude_players"))

    simulator = sim.MatchSimulator(home_team_id=home_team_id,
                                   away_team_id=away_team_id,
                                   season=selected_season,
                                   exclude_penalties=include_penalties,
                                   use_psxg=use_psxg,
                                   home_advantage=home_advantage,
                                   away_advantage=away_advantage,
                                   excluded_player_ids=excluded_player_ids)
    simulator.run_simulations(n_simulations)

    summary = simulator.get_summary()
    scorelines = simulator.get_scoreline_distribution()
    home_scorers = simulator.get_top_scorers("home", limit = 5)
    away_scorers = simulator.get_top_scorers("away", limit = 5)

    return render_template('simulation_results.html',
                            summary=summary,
                            scorelines=scorelines,
                            home_scorers=home_scorers,
                            away_scorers=away_scorers,
                            n_simulations=n_simulations,
                            use_psxg=use_psxg,
                            exclude_penalties=include_penalties,
                            season=selected_season,
                            seasons = SEASONS)

@app.route("/blog")
@nocache
def blog():
    selected_season = get_selected_season()
    posts = load_blog_posts()
    subheaders = [
        "If it looks smart, it was probably an accident.",
        "Because yelling at data is cheaper than therapy.",
        "From numbers to nonsense in record time.",
        "Bringing data to life and then arguing with it.",
        "I swear this made sense in my head.",
        "A broken model is still right twice a season.",
        "Every few posts, I nail it.",
        "Sometimes I connect the dots. Sometimes I just draw circles.",
        "Every now and then I have a good idea."
    ]
    return render_template("blog.html",
                           posts=posts,
                           subheader=random.choice(subheaders),
                           season=selected_season,
                           seasons = SEASONS)

@app.route("/blog/<slug>")
@nocache
def blog_post(slug):
    selected_season = get_selected_season()
    post = get_post_by_slug(slug)
    if not post:
        abort(404)

    html_body = markdown.markdown(
        post["body"],
        extensions=["fenced_code", "tables", "attr_list"]
    )

    meta = {
        "title": post["title"],
        "description": post["excerpt"],
        "image": url_for('static', filename=post["featured_image"], _external=True),
        "url": request.url,
    }

    return render_template("blog_post.html",
                           post=post,
                           html_body=html_body,
                           meta=meta,
                           season=selected_season,
                           seasons = SEASONS)


def _insert_event_markers(shot_data, home_team_id, away_team_id):
    new_data = []
    halftime_inserted = False

    for i, shot in enumerate(shot_data):
        if i == 0:
            # Handle edge case: first shot is not a goal but score has changed
            if shot['goal'] == 0 and (shot['home_score'] != 0 or shot['away_score'] != 0):
                if shot['home_score'] > 0:
                    benefiting_team_id = home_team_id
                elif shot['away_score'] > 0:
                    benefiting_team_id = away_team_id
                else:
                    benefiting_team_id = 'Unknown'

                own_goal_marker = {
                    'type': 'own_goal',
                    'home_score': shot['home_score'],
                    'away_score': shot['away_score'],
                    'expanded_minute': shot['expanded_minute'],
                    'period_id': shot['period_id'],
                    'team_id': benefiting_team_id
                }
                new_data.append(own_goal_marker)

        else:
            prev_shot = shot_data[i - 1]
            score_changed = (
                shot['home_score'] != prev_shot['home_score'] or
                shot['away_score'] != prev_shot['away_score']
            )
            both_no_goals = prev_shot['goal'] == 0 and shot['goal'] == 0

            if score_changed and both_no_goals:
                if shot['home_score'] > prev_shot['home_score']:
                    benefiting_team_id = home_team_id
                elif shot['away_score'] > prev_shot['away_score']:
                    benefiting_team_id = away_team_id
                else:
                    benefiting_team_id = 'Unknown'

                own_goal_marker = {
                    'type': 'own_goal',
                    'home_score': shot['home_score'],
                    'away_score': shot['away_score'],
                    'expanded_minute': shot['expanded_minute'],
                    'period_id': shot['period_id'],
                    'team_id': benefiting_team_id
                }
                new_data.append(own_goal_marker)

        if not halftime_inserted and shot['period_id'] == 2:
            new_data.append({
                'type': 'halftime',
                'home_score': shot['home_score'],
                'away_score': shot['away_score']
            })
            halftime_inserted = True

        new_data.append(shot)

    if shot_data:
        final_shot = shot_data[-1]
        new_data.append({
            'type': 'fulltime',
            'home_score': final_shot['home_score'],
            'away_score': final_shot['away_score']
        })
    return new_data

def get_selected_season():
    return session.get('season', datetime.now().year)


if __name__ == '__main__':
    app.run(debug=True)
