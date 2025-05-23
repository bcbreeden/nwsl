from flask import Flask, render_template, request, redirect, url_for
from data import (db_games_xgoals, db_games, db_goalkeeper_goals_added,db_goalkeeper_xgoals,
                db_player_goals_added, db_player_info, db_player_xgoals, db_player_xpass,
                db_setup, db_team_goals_added, db_team_info, db_team_xgoals, db_team_xpass, db_game_flow,
                db_stadium_info)
from plots import plot_spider, plot_deviation_from_average_chart, plot_team_strength_donut, get_donut_plot_for_team_results
from momentum_plot import generate_momentum_plot
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime

app = Flask(__name__)
app.config["DEBUG"] = True

class SeasonManager:
    def __init__(self):
        self.season = datetime.now().year
        self.seasons = [2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016]

    def set_season(self, new_season):
        self.season = int(new_season)

season_manager = SeasonManager()

'''
Renders the index template.
'''
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_season = request.form.get('season_year')
        season_manager.set_season(new_season)
    teams_data = db_team_xgoals.get_top_team_xgoals_stat(season_manager.season, 'points')
    top_5_goalscorers = db_player_xgoals.get_top_player_xgoals_stat(season_manager.season, 'goals', 5)
    top_5_assists = db_player_xgoals.get_top_player_xgoals_stat(season_manager.season, 'primary_assists', 5)
    shots_on_target = db_player_xgoals.get_player_xgoals_minimum_shots(season_manager.season, 'shots_on_target_perc', 5, 10)
    total_shots = db_player_xgoals.get_top_player_xgoals_stat(season_manager.season, 'shots', 5)
    minutes_played_df = db_player_xgoals.get_defender_minutes_played(season_manager.season, 'minutes_played', 5)
    minutes_played_non_df = db_player_xgoals.get_minutes_played_non_df(season_manager.season, 'minutes_played', 5)
    return render_template('index.html',
                           teams_data = teams_data,
                           top_scorers = top_5_goalscorers,
                           top_assists = top_5_assists,
                           shots_on_target = shots_on_target,
                           minutes_played_df = minutes_played_df,
                           minutes_played_non_df = minutes_played_non_df,
                           total_shots = total_shots,
                           season = season_manager.season,
                           seasons = season_manager.seasons)

@app.route('/league')
def league():
    top_5_goalscorers = db_player_xgoals.get_top_player_xgoals_stat(season_manager.season, 'goals', 5)
    top_5_assists = db_player_xgoals.get_top_player_xgoals_stat(season_manager.season, 'primary_assists', 5)
    shots_on_target = db_player_xgoals.get_player_xgoals_minimum_shots(season_manager.season, 'shots_on_target_perc', 5, 10)
    total_shots = db_player_xgoals.get_top_player_xgoals_stat(season_manager.season, 'shots', 5)
    minutes_played_df = db_player_xgoals.get_defender_minutes_played(season_manager.season, 'minutes_played', 5)
    minutes_played_non_df = db_player_xgoals.get_minutes_played_non_df(season_manager.season, 'minutes_played', 5)
    return render_template('league.html',
                            top_scorers = top_5_goalscorers,
                            top_assists = top_5_assists,
                            shots_on_target = shots_on_target,
                            minutes_played_df = minutes_played_df,
                            minutes_played_non_df = minutes_played_non_df,
                            total_shots = total_shots,
                            season = season_manager.season,
                            seasons = season_manager.seasons)

@app.route('/teams')
def teams():
    team_data = db_team_xgoals.get_top_team_xgoals_stat(season_manager.season, 'team_strength')
    team_strength_history = db_team_xgoals.get_team_strength_by_season(season_manager.season)
    return render_template('teams.html',
                           teams = team_data,
                           team_strength_history = team_strength_history,
                           season = season_manager.season,
                           seasons = season_manager.seasons)

@app.route('/team', methods=['GET', 'POST'])
def team():
    if request.method == 'POST':
        team_id = request.form.get('team_id')
        obj_id = request.form.get('obj_id')
        team_xgoals_data = db_team_xgoals.get_team_xgoals_by_season(team_id, season_manager.season)
        team_xpass_data = db_team_xpass.get_team_xpass_by_season(team_id, season_manager.season)
        team_goals_added_data = db_team_goals_added.get_team_goals_added_by_season(team_id, season_manager.season)

        team_strength = team_xgoals_data['team_strength']
        strength_fig_json, strength_config = plot_team_strength_donut(team_strength)

        team_record = db_games.get_team_record_by_season(team_id, season_manager.season)
        game_results = db_games.get_team_game_results(team_id, season_manager.season)
        five_recent_games = game_results[:5][::-1]

        stadium = db_stadium_info.get_stadium_by_id(db_games.get_most_recent_home_stadium_id(team_id, season_manager.season))

        results_fig_json, results_config = get_donut_plot_for_team_results(
                                                                        team_record['wins'],
                                                                        team_record['losses'],
                                                                        team_record['draws'],
                                                                        team_xgoals_data['points']
                                                                        )

        return render_template('team.html',
                                team_xgoals_data = team_xgoals_data,
                                season = season_manager.season,
                                seasons = season_manager.seasons,
                                strength_fig_json = strength_fig_json, 
                                strength_config = strength_config,
                                team_record = team_record,
                                game_results = game_results,
                                five_recent_games = five_recent_games,
                                stadium = stadium,
                                results_fig_json = results_fig_json,
                                results_config = results_config)
    if request.method == 'GET':
        redirect(url_for('teams'))


@app.route('/team_comparison', methods=['GET', 'POST'])
def team_comparison():
    team_data = db_team_xgoals.get_top_team_xgoals_stat(season_manager.season, 'points')
    team1_id = request.form.get('team1')
    team2_id = request.form.get('team2')
    team1_data = db_team_xgoals.get_team_xgoals_by_season(team1_id, season_manager.season)
    team2_data = db_team_xgoals.get_team_xgoals_by_season(team2_id, season_manager.season)
    ordered_stats = [
        {'name': 'count_games', 'label': 'Matches Played', 'type': 'neutral'},
        {'name': 'team_strength', 'label': 'Team Strength', 'type': 'positive'},
        {'name': 'shots_for', 'label': 'Shots For', 'type': 'positive'},
        {'name': 'shots_against', 'label': 'Shots Against', 'type': 'negative'},
        {'name': 'goals_for', 'label': 'Goals For', 'type': 'positive'},
        {'name': 'goals_against', 'label': 'Goals Against', 'type': 'negative'},
        {'name': 'goal_difference', 'label': 'Goal Differential', 'type': 'positive'},
        {'name': 'xgoals_for', 'label': 'xGoals For', 'type': 'positive'},
        {'name': 'xgoals_against', 'label': 'xGoals Against', 'type': 'negative'},
        {'name': 'xgoal_difference', 'label': 'xGoals Differential', 'type': 'positive'},
        {'name': 'goal_difference_minus_xgoal_difference', 'label': 'Goal Diff - xGoal Diff', 'type': 'neutral'},
        {'name': 'points', 'label': 'Points', 'type': 'positive'},
        {'name': 'xpoints', 'label': 'xPoints', 'type': 'positive'},
        # {'name': 'point_diff', 'label': 'Point Differential', 'type': 'neutral'},
        {'name': 'goalfor_xgoalfor_diff', 'label': 'Goal For | xGoal For Diff', 'type': 'positive'}
    ]

    return render_template('team_comparison.html',
                            team1_data = team1_data,
                            team2_data = team2_data,
                            ordered_stats = ordered_stats,
                            teams = team_data,
                            season = season_manager.season,
                            seasons = season_manager.seasons)

@app.route('/games')
def games():
    games_data = db_games.get_all_games_by_season(season_manager.season)
    games_xgoals_data = db_games_xgoals.get_all_games_xgoals_by_season(season_manager.season)
    return render_template('games.html',
                           games_data = games_data,
                           games_xgoals_data = games_xgoals_data,
                           season = season_manager.season,
                           seasons = season_manager.seasons)

@app.route('/game', methods=['GET', 'POST'])
def game():
    if request.method == 'POST':
        game_data = db_games.get_game_by_id(request.form.get('game_id'))
        game_xgoals_data = db_games_xgoals.get_game_xgoals_by_id(request.form.get('game_id'))
        game_flow_data = db_game_flow.get_game_flow_by_game_id(request.form.get('game_id'))

        game_flow_json, game_flow_config = generate_momentum_plot(request.form.get('game_id'))
        return render_template('game.html',
                                game_data = game_data,
                                game_xgoals_data = game_xgoals_data,
                                game_flow_data = game_flow_data,
                                game_flow_json = game_flow_json, 
                                game_flow_config = game_flow_config,
                                season = season_manager.season,
                                seasons = season_manager.seasons)
    else:
        return redirect(url_for('games'))

@app.route('/players')
def players():
    players_xgoals_data = db_player_xgoals.get_top_player_xgoals_stat(season_manager.season)
    players_xpass_data = db_player_xpass.get_all_player_xpass(season_manager.season)

    combined_data = zip(players_xgoals_data, players_xpass_data)
    return render_template('players.html',
                           player_data = combined_data,
                           season = season_manager.season,
                           seasons = season_manager.seasons)

@app.route('/player', methods=['GET', 'POST'])
def player():
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
        
        player_xgoals_data = db_player_xgoals.get_player_xgoal_data(player_id, season_manager.season)
        player_xpass_data = db_player_xpass.get_player_xpass(player_id, season_manager.season)
        player_goals_added_data = db_player_goals_added.get_player_goals_added_by_season(player_id, season_manager.season)
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
                               season = season_manager.season,
                               seasons = season_manager.seasons,
                               player_season_data = player_xgoals_all_seasons_data)
    return redirect(url_for('players'))

@app.route('/goalkeepers', methods=['GET', 'POST'])
def goalkeepers():
    goalkeeper_data = db_goalkeeper_xgoals.get_all_goalkeepers_xgoals_by_season(season_manager.season)
    return render_template('goalkeepers.html',
                           keeper_data = goalkeeper_data,
                           season = season_manager.season,
                           seasons = season_manager.seasons)

@app.route('/goalkeeper', methods=['GET', 'POST'])
def goalkeeper():
    if request.method == 'POST':
        player_id = request.form.get('player_id')
        obj_id = request.form.get('obj_id')
        keeper_xgoal_data = db_goalkeeper_xgoals.get_goalkeeper_xgoals_by_season(player_id=player_id, season=season_manager.season)
        keeper_goals_added_data = db_goalkeeper_goals_added.get_goalkeeper_goals_added_by_season(player_id=player_id, season=season_manager.season)
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
                                season = season_manager.season,
                                seasons = season_manager.seasons)
    
    goalkeeper_data = db_goalkeeper_xgoals.get_all_goalkeepers_xgoals_by_season(season_manager.season)
    return render_template('goalkeepers.html',
                           keeper_data = goalkeeper_data,
                           season = season_manager.season,
                           seasons = season_manager.seasons)

if __name__ == '__main__':
    app.run(debug=True)
