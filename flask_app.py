from flask import Flask, render_template, request, redirect, url_for
from data import (db_games_xgoals, db_games, db_goalkeeper_goals_added,db_goalkeeper_xgoals,
                db_player_goals_added, db_player_info, db_player_xgoals, db_player_xpass,
                db_setup, db_team_goals_added, db_team_info, db_team_xgoals, db_team_xpass)
from plots import plot_team_goals_points, plot_team_points_diff, plot_goal_vs_xgoal, plot_spider
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime

app = Flask(__name__)
app.config["DEBUG"] = True

class SeasonManager:
    def __init__(self):
        self.season = datetime.now().year
        self.seasons = [2025, 2024, 2023, 2022, 2021, 2020, 2019]

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
    team_points_data = db_team_xgoals.get_top_team_xgoals_stat(season_manager.season, 'points')
    top_5_goalscorers = db_player_xgoals.get_top_player_xgoals_stat(season_manager.season, 'goals', 5)
    top_5_assists = db_player_xgoals.get_top_player_xgoals_stat(season_manager.season, 'primary_assists', 5)
    shots_on_target = db_player_xgoals.get_player_xgoals_minimum_shots(season_manager.season, 'shots_on_target_perc', 5, 10)
    total_shots = db_player_xgoals.get_top_player_xgoals_stat(season_manager.season, 'shots', 5)
    minutes_played_df = db_player_xgoals.get_defender_minutes_played(season_manager.season, 'minutes_played', 5)
    minutes_played_non_df = db_player_xgoals.get_minutes_played_non_df(season_manager.season, 'minutes_played', 5)
    return render_template('index.html',
                           team_points_data = team_points_data,
                           top_scorers = top_5_goalscorers,
                           top_assists = top_5_assists,
                           shots_on_target = shots_on_target,
                           minutes_played_df = minutes_played_df,
                           minutes_played_non_df = minutes_played_non_df,
                           total_shots = total_shots,
                           season = season_manager.season,
                           seasons =season_manager.seasons)

@app.route('/teams')
def teams():
    team_data = db_team_xgoals.get_top_team_xgoals_stat(season_manager.season, 'points')
    plt_team_goals_points = plot_team_goals_points()
    plt_team_goals_points_html = pio.to_html(plt_team_goals_points, full_html=False)
    plt_team_points_diff = plot_team_points_diff()
    plt_team_points_diff_html = pio.to_html(plt_team_points_diff, full_html=False)
    plt_team_goal_xgoal_diff = plot_goal_vs_xgoal()
    plt_team_goal_xgoal_diff_html =  pio.to_html(plt_team_goal_xgoal_diff, full_html=False)
    return render_template('teams.html',
                           teams = team_data,
                           team_goal_point_plot = plt_team_goals_points_html,
                           team_points_dif_plot = plt_team_points_diff_html,
                           team_goal_xgoal_diff_plot = plt_team_goal_xgoal_diff_html,
                           season = season_manager.season,
                           seasons = season_manager.seasons)

@app.route('/games')
def games():
    return render_template('games.html',
                           season = season_manager.season,
                           seasons = season_manager.seasons)

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

        xgoals_fig_json, xgoals_config = plot_spider(x_goals_stats_to_plot, player_xgoals_data)
        xpass_fig_json, xpass_config = plot_spider(x_pass_stats_to_plot, player_xpass_data)
        defense_fig_json, defense_config = plot_spider(defense_to_plot, player_goals_added_data, 9)
        
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
                               seasons = season_manager.seasons)
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
        
        combined_data = {**keeper_xgoal_data, **keeper_goals_added_data}

        # This value needs to be inverted since a negative value is better than a positive one
        combined_data["goals_minus_xgoals_gk"] = abs(combined_data["goals_minus_xgoals_gk"])
        
        stats_to_plot = ['goals_minus_xgoals_gk', 'shotstopping_goals_added_above_avg', 'handling_goals_added_above_avg', 'claiming_goals_added_above_avg',
                         'sweeping_goals_added_above_avg', 'passing_goals_added_above_avg']
        keeper_fig_json, keeper_config = plot_spider(stats_to_plot, combined_data)
        

        return render_template('goalkeeper.html',
                                player_id = player_id,
                                obj_id = obj_id,
                                keeper_xgoal_data  = keeper_xgoal_data,
                                keeper_goals_added_data = keeper_goals_added_data,
                                keeper_fig_json = keeper_fig_json,
                                keeper_config = keeper_config,
                                season = season_manager.season,
                                seasons = season_manager.seasons)
    
    goalkeeper_data = db_goalkeeper_xgoals.get_all_goalkeepers_xgoals_by_season(season_manager.season)
    return render_template('goalkeepers.html',
                           keeper_data = goalkeeper_data,
                           season = season_manager.season,
                           seasons = season_manager.seasons)

if __name__ == '__main__':
    app.run(debug=True)
