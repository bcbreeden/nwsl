from api import make_asa_api_call
import sqlite3

def insert_player_xpass_by_season(season):
    print('Inserting data for players (xpass) for season:', season)
    api_string = 'nwsl/players/xpass?season_name={}&stage_name=Regular Season'.format(str(season))
    players_data = make_asa_api_call(api_string)[1]
    conn = sqlite3.connect('data/nwsl.db')
    cursor = conn.cursor()
    for player in players_data:
        player_id = player.get('player_id', 'Unknown Player ID')
        obj_id = player_id + str(season)
        team_id = player.get('team_id', [])
        general_position = player.get('general_position', 'Unknown General Position')
        minutes_played = player.get('minutes_played', 0)
        attempted_passes = player.get('attempted_passes', 0)
        pass_completion_percentage = player.get('pass_completion_percentage', 0.0)
        xpass_completion_percentage = player.get('xpass_completion_percentage', 0.0)
        passes_completed_over_expected = player.get('passes_completed_over_expected', 0.0)
        passes_completed_over_expected_p100 = player.get('passes_completed_over_expected_p100', 0.0)
        avg_distance_yds = player.get('avg_distance_yds', 0.0)
        avg_vertical_distance_yds = player.get('avg_vertical_distance_yds', 0.0)
        share_team_touches = player.get('share_team_touches', 0.0)
        count_games = player.get('count_games', 0)
        

        if isinstance(team_id, list):
            team_id = team_id[-1]
        elif isinstance(team_id, str):
            pass
        else:
            print('No team associated with player:', player_id)

        cursor.execute('''
            INSERT OR REPLACE INTO player_xpass (
                id, player_id, team_id, general_position, minutes_played, attempted_passes,
                pass_completion_percentage, xpass_completion_percentage, passes_completed_over_expected,
                passes_completed_over_expected_p100, avg_distance_yds, avg_vertical_distance_yds,
                share_team_touches, count_games, season
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?, ?, ?
            )
        ''', (
            obj_id, player_id, team_id, general_position, minutes_played, attempted_passes, pass_completion_percentage,
            xpass_completion_percentage, passes_completed_over_expected, passes_completed_over_expected_p100,
            avg_distance_yds, avg_vertical_distance_yds, share_team_touches, count_games, int(season)
        ))
        conn.commit()
    conn.close()

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