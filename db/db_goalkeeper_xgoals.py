from api import make_api_call
import sqlite3

def insert_goalkeeper_xgoals_by_season(season):
    print('Inserting goalkeeper xgoals by season for:', season)
    api_string = 'nwsl/goalkeepers/xgoals?season_name={}'.format(str(season))
    players_data = make_api_call(api_string)[1]
    conn = sqlite3.connect('db/nwsl.db')
    cursor = conn.cursor()
    for player in players_data:
        player_id = player.get('player_id', 'Unknown Player ID')
        team_id = player.get('team_id', 'Unknown Team ID')
        minutes_played = player.get('minutes_played', 0)
        shots_faced = player.get('shots_faced', 0)
        goals_conceded = player.get('goals_conceded', 0)
        saves = player.get('saves', 0)
        share_headed_shots = player.get('share_headed_shots', 0.0)
        xgoals_gk_faced = player.get('xgoals_gk_faced', 0.0)
        goals_minus_xgoals_gk = player.get('goals_minus_xgoals_gk', 0.0)
        goals_divided_by_xgoals_gk = player.get('goals_divided_by_xgoals_gk', 0.0)

        cursor.execute('''
            INSERT OR REPLACE INTO goalkeeper_xgoals (
                player_id, team_id, minutes_played, shots_faced, goals_conceded, 
                saves, share_headed_shots, xgoals_gk_faced, goals_minus_xgoals_gk, 
                goals_divided_by_xgoals_gk, season
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
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
    conn = sqlite3.connect('db/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM goalkeeper_xgoals WHERE season = ?', (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('All goalkeepers returned with xgoal data.')
    return rows

def get_goalkeeper_xgoals_by_season(player_id, season):
    print('Fetching goalkeeper xgoals for season: {}'.format(season))
    conn = sqlite3.connect('db/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM goalkeeper_xgoals WHERE season = ? and player_id = ?', (season, player_id))
    rows = cursor.fetchone()
    conn.commit()
    conn.close()
    print('Goalkeeper returned with xgoal data.')
    return rows