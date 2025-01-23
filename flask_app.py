from flask import Flask, render_template, request
from data import (db_games_xgoals, db_games, db_goalkeeper_goals_added,db_goalkeeper_xgoals,
                db_player_goals_added, db_player_info, db_player_xgoals, db_player_xpass,
                db_setup, db_team_goals_added, db_team_info, db_team_xgoals, db_team_xpass)
from plots import plot_team_goals_points, plot_team_points_diff, plot_goal_vs_xgoal, plot_spider
import plotly.graph_objects as go
import plotly.io as pio

app = Flask(__name__)
app.config["DEBUG"] = True

'''
Renders the index template.
'''
@app.route('/')
def index():
    team_points_data = db_team_xgoals.get_top_team_xgoals_stat(2024, 'points')
    top_5_goalscorers = db_player_xgoals.get_top_player_xgoals_stat(2024, 'goals', 5)
    top_5_assists = db_player_xgoals.get_top_player_xgoals_stat(2024, 'primary_assists', 5)
    shots_on_target = db_player_xgoals.get_player_xgoals_minimum_shots(2024, 'shots_on_target_perc', 5, 10)
    total_shots = db_player_xgoals.get_top_player_xgoals_stat(2024, 'shots', 5)
    minutes_played_df = db_player_xgoals.get_defender_minutes_played(2024, 'minutes_played', 5)
    minutes_played_non_df = db_player_xgoals.get_minutes_played_non_df(2024, 'minutes_played', 5)
    return render_template('index.html',
                           team_points_data = team_points_data,
                           top_scorers = top_5_goalscorers,
                           top_assists = top_5_assists,
                           shots_on_target = shots_on_target,
                           minutes_played_df = minutes_played_df,
                           minutes_played_non_df = minutes_played_non_df,
                           total_shots = total_shots)

@app.route('/teams')
def teams():
    team_data = db_team_xgoals.get_top_team_xgoals_stat(2024, 'points')
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
                           team_goal_xgoal_diff_plot = plt_team_goal_xgoal_diff_html)

@app.route('/games')
def games():
    return render_template('games.html')

@app.route('/players')
def players():
    players_xgoals_data = db_player_xgoals.get_all_player_xgoals(2024)
    players_xpass_data = db_player_xpass.get_all_player_xpass(2024)

    combined_data = zip(players_xgoals_data, players_xpass_data)
    return render_template('players.html',
                           player_data = combined_data)

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
        player_id = request.form.get('player_id')
        obj_id = request.form.get('obj_id')
        player_xgoals_data = db_player_xgoals.get_player_xgoal_data(player_id, 2024)
        player_xpass_data = db_player_xpass.get_player_xpass(player_id, 2024)
        xgoals_fig_json, xgoals_config = plot_spider(x_goals_stats_to_plot, player_xgoals_data)
        xpass_fig_json, xpass_config = plot_spider(x_pass_stats_to_plot, player_xpass_data)
        player_goals_added_data = db_player_goals_added.get_player_goals_added_by_season(player_id, 2024)
        return render_template('player.html',
                               player_id = player_id,
                               obj_id = obj_id,
                               player_xgoals_data = player_xgoals_data,
                               player_xpass_data = player_xpass_data,
                               player_goals_added_data = player_goals_added_data,
                               xgoals_fig_json = xgoals_fig_json,
                               xgoals_config = xgoals_config,
                               xpass_fig_json = xpass_fig_json,
                               xpass_config = xpass_config)
    player_data = db_player_xgoals.get_all_player_xgoals(2024)
    return render_template('players.html',
                           players = player_data)

@app.route('/goalkeepers')
def goalkeepers():
    return render_template('goalkeepers.html')

if __name__ == '__main__':
    app.run(debug=True)
