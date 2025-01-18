from api import make_asa_api_call
import sqlite3
from collections import defaultdict

def insert_player_xpass_by_season(season):
    print(f'Inserting data for players (xpass) for season: {season}')
    
    # Fetch player data
    api_string = f'nwsl/players/xpass?season_name={season}&stage_name=Regular Season'
    players_data = make_asa_api_call(api_string)[1]
    conn = sqlite3.connect('data/nwsl.db')
    cursor = conn.cursor()

    # Filter out goalkeepers
    players_data = [player for player in players_data if player.get('general_position') != 'GK']

    # Filter out players with less than 200 minutes played for averages
    filtered_for_averages = [player for player in players_data if player.get('minutes_played', 0) >= 200]

    # Group players by position and calculate sums and counts
    position_sums = defaultdict(lambda: defaultdict(float))
    position_counts = defaultdict(int)

    for player in filtered_for_averages:
        position = player.get('general_position', 'Unknown General Position')
        position_counts[position] += 1
        position_sums[position]['minutes_played'] += player.get('minutes_played', 0)
        position_sums[position]['attempted_passes'] += player.get('attempted_passes', 0)
        position_sums[position]['pass_completion_percentage'] += round((player.get('pass_completion_percentage', 0.0) * 100), 2)
        position_sums[position]['xpass_completion_percentage'] += round((player.get('xpass_completion_percentage', 0.0) * 100), 2)
        position_sums[position]['passes_completed_over_expected'] += round(player.get('passes_completed_over_expected', 0.0), 2)
        position_sums[position]['passes_completed_over_expected_p100'] += round(player.get('passes_completed_over_expected_p100', 0.0), 2)
        position_sums[position]['avg_distance_yds'] += round(player.get('avg_distance_yds', 0.0), 2)
        position_sums[position]['avg_vertical_distance_yds'] += round(player.get('avg_vertical_distance_yds', 0.0), 2)
        position_sums[position]['share_team_touches'] += round((player.get('share_team_touches', 0.0) * 100), 2)
        position_sums[position]['count_games'] += player.get('count_games', 0)

    # Calculate averages for each position
    position_averages = {
        position: {f"avg_{key}": round(value / position_counts[position], 2) for key, value in sums.items()}
        for position, sums in position_sums.items()
    }

    # Insert data for each player
    for player in players_data:
        player_id = player.get('player_id', 'Unknown Player ID')
        obj_id = player_id + str(season)
        team_id = player.get('team_id', [])
        general_position = player.get('general_position', 'Unknown General Position')
        minutes_played = player.get('minutes_played', 0)
        attempted_passes = player.get('attempted_passes', 0)
        pass_completion_percentage = round((player.get('pass_completion_percentage', 0.0) * 100), 2)
        xpass_completion_percentage = round((player.get('xpass_completion_percentage', 0.0) * 100), 2)
        passes_completed_over_expected = round(player.get('passes_completed_over_expected', 0.0), 2)
        passes_completed_over_expected_p100 = round(player.get('passes_completed_over_expected_p100', 0.0), 2)
        avg_distance_yds = round(player.get('avg_distance_yds', 0.0), 2)
        avg_vertical_distance_yds = round(player.get('avg_vertical_distance_yds', 0.0), 2)
        share_team_touches = round((player.get('share_team_touches', 0.0) * 100), 2)
        count_games = player.get('count_games', 0)

        if isinstance(team_id, list):
            team_id = team_id[-1]

        # Get position-specific averages or set default values
        position_avg = position_averages.get(
            general_position, {f"avg_{key}": 0 for key in position_sums['Unknown General Position'].keys()}
        )

        cursor.execute('''
            INSERT OR REPLACE INTO player_xpass (
                id, player_id, team_id, general_position, minutes_played, attempted_passes,
                pass_completion_percentage, xpass_completion_percentage, passes_completed_over_expected,
                passes_completed_over_expected_p100, avg_distance_yds, avg_vertical_distance_yds,
                share_team_touches, count_games, season,
                avg_minutes_played, avg_attempted_passes, avg_pass_completion_percentage,
                avg_xpass_completion_percentage, avg_passes_completed_over_expected, 
                avg_passes_completed_over_expected_p100, avg_avg_distance_yds, avg_avg_vertical_distance_yds, 
                avg_share_team_touches, avg_count_games
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            obj_id, player_id, team_id, general_position, minutes_played, attempted_passes, pass_completion_percentage,
            xpass_completion_percentage, passes_completed_over_expected, passes_completed_over_expected_p100,
            avg_distance_yds, avg_vertical_distance_yds, share_team_touches, count_games, int(season),
            position_avg['avg_minutes_played'], position_avg['avg_attempted_passes'], 
            position_avg['avg_pass_completion_percentage'], position_avg['avg_xpass_completion_percentage'],
            position_avg['avg_passes_completed_over_expected'], position_avg['avg_passes_completed_over_expected_p100'],
            position_avg['avg_avg_distance_yds'], position_avg['avg_avg_vertical_distance_yds'], 
            position_avg['avg_share_team_touches'], position_avg['avg_count_games']
        ))

    conn.commit()
    conn.close()
    print(f'Player xpass data for season {season} inserted with position-specific averages.')


def get_player_xpass(player_id, season):
    print('Fetching player xpass for:{}, Season: {}'.format(player_id, season))
    obj_id = player_id + str(season)
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