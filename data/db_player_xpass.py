from api import make_asa_api_call
from .data_util import aggregate_position_data, generate_player_season_id, MINIMUM_MINUTES
import sqlite3

def insert_player_xpass_by_season(season, conn=None):
    """
    Main function to fetch, process, and insert player xGoals data.

    Args:
        season (int): The season year.
        conn (sqlite3.Connection, optional): Database connection. Defaults to None.

    Returns:
        None
    """
    print(f'Inserting data for players (xpass) for season: {season}')
    close_connection = False
    if conn is None:
        conn = sqlite3.connect('data/nwsl.db')
        close_connection = True

    stats_to_track = [
    'minutes_played', 'attempted_passes', 'pass_completion_percentage', 'xpass_completion_percentage',
    'passes_completed_over_expected', 'passes_completed_over_expected_p100', 'avg_distance_yds',
    'avg_vertical_distance_yds', 'share_team_touches', 'count_games'
    ]

    players_data = fetch_players_xpass_data(season, excluded_positions=['GK'])
    filtered_players = calculate_player_statistics(players_data)
    position_data = aggregate_position_data(filtered_players, stats_to_track)
    insert_player_data(conn, players_data, position_data, stats_to_track, season)

    if close_connection:
        conn.close()
    print(f'Player xpass data for season {season} inserted successfully.')

def calculate_player_statistics(players_data: list):
    stats_to_calculate = ['pass_completion_percentage', 'xpass_completion_percentage', 'share_team_touches']
    for player in players_data:
        for stat in stats_to_calculate:
            stat_value = player.get(stat, 0)
            player[stat] = round((stat_value * 100), 2)
    return [player for player in players_data if player.get('minutes_played', 0) >= MINIMUM_MINUTES]

def fetch_players_xpass_data(season: int, excluded_positions: list = None):
    if excluded_positions is None:
        excluded_positions = ['']

    api_string = f'nwsl/players/xpass?season_name={season}&stage_name=Regular Season'
    players_data = make_asa_api_call(api_string)[1]

    # Filter out passed in positions and return
    return [player for player in players_data if player.get('general_position') not in excluded_positions]

def insert_player_data(conn, players_data, position_data, stats_to_track, season):
    cursor = conn.cursor()

    for player in players_data:
        player_id = player.get('player_id', 'Unknown Player ID')
        obj_id = generate_player_season_id(player_id=player_id, season=str(season))
        team_id = player.get('team_id', [])
        general_position = player.get('general_position', 'Unknown General Position')
        minutes_played = player.get('minutes_played', 0)
        attempted_passes = player.get('attempted_passes', 0)
        pass_completion_percentage = player.get('pass_completion_percentage', 0.0)
        xpass_completion_percentage = player.get('xpass_completion_percentage', 0.0)
        passes_completed_over_expected = round(player.get('passes_completed_over_expected', 0.0), 2)
        passes_completed_over_expected_p100 = round(player.get('passes_completed_over_expected_p100', 0.0), 2)
        avg_distance_yds = round(player.get('avg_distance_yds', 0.0), 2)
        avg_vertical_distance_yds = round(player.get('avg_vertical_distance_yds', 0.0), 2)
        share_team_touches = player.get('share_team_touches', 0.0)
        count_games = player.get('count_games', 0)

        if isinstance(team_id, list):
            team_id = team_id[-1]

        # Prepare player stats and round values
        position_avg = {f"avg_{stat}": round(position_data.get(general_position, {}).get(f"avg_{stat}", 0), 2) for stat in stats_to_track}
        position_min = {f"min_{stat}": round(position_data.get(general_position, {}).get(f"min_{stat}", 0), 2) for stat in stats_to_track}
        position_max = {f"max_{stat}": round(position_data.get(general_position, {}).get(f"max_{stat}", 0), 2) for stat in stats_to_track}
        

        cursor.execute('''
            INSERT OR REPLACE INTO player_xpass (
                id, player_id, team_id, general_position, minutes_played, attempted_passes,
                pass_completion_percentage, xpass_completion_percentage, passes_completed_over_expected,
                passes_completed_over_expected_p100, avg_distance_yds, avg_vertical_distance_yds,
                share_team_touches, count_games, season,
                avg_minutes_played, min_minutes_played, max_minutes_played,
                avg_attempted_passes, min_attempted_passes, max_attempted_passes,
                avg_pass_completion_percentage, min_pass_completion_percentage, max_pass_completion_percentage,
                avg_xpass_completion_percentage, min_xpass_completion_percentage, max_xpass_completion_percentage,
                avg_passes_completed_over_expected, min_passes_completed_over_expected, max_passes_completed_over_expected,
                avg_passes_completed_over_expected_p100, min_passes_completed_over_expected_p100, max_passes_completed_over_expected_p100,
                avg_avg_distance_yds, min_avg_distance_yds, max_avg_distance_yds,
                avg_avg_vertical_distance_yds, min_avg_vertical_distance_yds, max_avg_vertical_distance_yds,
                avg_share_team_touches, min_share_team_touches, max_share_team_touches,
                avg_count_games, min_count_games, max_count_games
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            obj_id, player_id, team_id, general_position, minutes_played, attempted_passes,
            pass_completion_percentage, xpass_completion_percentage, passes_completed_over_expected,
            passes_completed_over_expected_p100, avg_distance_yds, avg_vertical_distance_yds,
            share_team_touches, count_games, int(season),
            position_avg['avg_minutes_played'], position_min['min_minutes_played'], position_max['max_minutes_played'],
            position_avg['avg_attempted_passes'], position_min['min_attempted_passes'], position_max['max_attempted_passes'],
            position_avg['avg_pass_completion_percentage'], position_min['min_pass_completion_percentage'], position_max['max_pass_completion_percentage'],
            position_avg['avg_xpass_completion_percentage'], position_min['min_xpass_completion_percentage'], position_max['max_xpass_completion_percentage'],
            position_avg['avg_passes_completed_over_expected'], position_min['min_passes_completed_over_expected'], position_max['max_passes_completed_over_expected'],
            position_avg['avg_passes_completed_over_expected_p100'], position_min['min_passes_completed_over_expected_p100'], position_max['max_passes_completed_over_expected_p100'],
            position_avg['avg_avg_distance_yds'], position_min['min_avg_distance_yds'], position_max['max_avg_distance_yds'],
            position_avg['avg_avg_vertical_distance_yds'], position_min['min_avg_vertical_distance_yds'], position_max['max_avg_vertical_distance_yds'],
            position_avg['avg_share_team_touches'], position_min['min_share_team_touches'], position_max['max_share_team_touches'],
            position_avg['avg_count_games'], position_min['min_count_games'], position_max['max_count_games']
        ))

    conn.commit()

def get_player_xpass(player_id, season):
    print('Fetching player xpass for:{}, Season: {}'.format(player_id, season))
    obj_id = generate_player_season_id(player_id=player_id, season=str(season))
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = '''
        SELECT 
            pxp.*,
            pi.player_name,
            pi.player_first_name,
            pi.player_last_name,
            ti.team_name
            FROM 
                player_xpass AS pxp
            JOIN 
                player_info AS pi
            ON 
                pxp.player_id = pi.player_id
            JOIN
                team_info AS ti
            ON
                pxp.team_id = ti.team_id   
            WHERE
                pxp.id = ?;
        '''
    cursor.execute(query, (obj_id,))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    print('Player xpass returned.')
    return row

def get_all_player_xpass(season):
    print('Fetching all players xpass for season: {}'.format(season))
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = '''
        SELECT 
            pxp.*,
            pi.player_name,
            pi.player_first_name,
            pi.player_last_name,
            ti.team_name
            FROM 
                player_xpass AS pxp
            JOIN 
                player_info AS pi
            ON 
                pxp.player_id = pi.player_id
            JOIN
                team_info AS ti
            ON
                pxp.team_id = ti.team_id   
            WHERE
                pxp.season = ?;
        '''
    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('Player xpass returned.')
    return rows