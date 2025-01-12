from api import make_asa_api_call
import sqlite3

def insert_goalkeeper_xgoals_by_season(season):
    print('Inserting goalkeeper xgoals by season for:', season)
    api_string = 'nwsl/goalkeepers/xgoals?season_name={}&stage_name=Regular Season'.format(str(season))
    players_data = make_asa_api_call(api_string)[1]
    conn = sqlite3.connect('data/nwsl.db')
    cursor = conn.cursor()
    for player in players_data:
        player_id = player.get('player_id', 'Unknown Player ID')
        obj_id = player_id + str(season)
        team_id = player.get('team_id', 'Unknown Team ID')
        minutes_played = player.get('minutes_played', 0)
        shots_faced = player.get('shots_faced', 0)
        goals_conceded = player.get('goals_conceded', 0)
        saves = player.get('saves', 0)
        share_headed_shots = player.get('share_headed_shots', 0.0)
        xgoals_gk_faced = player.get('xgoals_gk_faced', 0.0)
        goals_minus_xgoals_gk = player.get('goals_minus_xgoals_gk', 0.0)
        goals_divided_by_xgoals_gk = player.get('goals_divided_by_xgoals_gk', 0.0)

        if isinstance(team_id, list):
            team_id = team_id[-1]
        elif isinstance(team_id, str):
            pass
        else:
            print('No team associated with player:', player_id)

        cursor.execute('''
            INSERT OR REPLACE INTO goalkeeper_xgoals (
                id, player_id, team_id, minutes_played, shots_faced, goals_conceded, 
                saves, share_headed_shots, xgoals_gk_faced, goals_minus_xgoals_gk, 
                goals_divided_by_xgoals_gk, season
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            obj_id,
            player_id,
            team_id,
            minutes_played,
            shots_faced,
            goals_conceded,
            saves,
            share_headed_shots,
            xgoals_gk_faced,
            goals_minus_xgoals_gk,
            goals_divided_by_xgoals_gk,
            int(season)
            ))
        conn.commit()
    cursor.close()
    conn.close()

def get_all_goalkeepers_xgoals_by_season(season):
    print('Fetching all goalkeepers xgoals for season: {}'.format(season))
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = '''
        SELECT 
            gx.*,
            pi.player_name,
            pi.player_first_name,
            pi.player_last_name,
            ti.team_name
            FROM 
                goalkeeper_xgoals AS gx
            JOIN 
                player_info AS pi
            ON 
                gx.player_id = pi.player_id
            JOIN
                team_info AS ti
            ON
                gx.team_id = ti.team_id   
            WHERE
                gx.season = ?
            ORDER BY
                gx.saves;
        '''
    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('All goalkeepers returned with xgoal data.')
    return rows

def get_goalkeeper_xgoals_by_season(player_id, season):
    print('Fetching goalkeeper xgoals for {} season: {}'.format(player_id, season))
    obj_id = player_id + str(season)
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    obj_id = player_id + str(season)
    query = f'''
        SELECT 
            gx.*,
            pi.player_name,
            pi.player_first_name,
            pi.player_last_name,
            ti.team_name
            FROM 
                goalkeeper_xgoals AS gx
            JOIN 
                player_info AS pi
            ON 
                gx.player_id = pi.player_id
            JOIN
                team_info AS ti
            ON
                gx.team_id = ti.team_id   
            WHERE
                gx.id = ?;
        '''
    cursor.execute(query, (obj_id,))
    rows = cursor.fetchone()
    conn.commit()
    conn.close()
    print('Goalkeeper returned with xgoal data.')
    return rows