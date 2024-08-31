from api import make_asa_api_call
import sqlite3

def insert_player_xgoals_by_season(season):
    print('Inserting data for players (xgoal) for season:', season)
    api_string = 'nwsl/players/xgoals?season_name={}'.format(str(season))
    players_data = make_asa_api_call(api_string)[1]
    conn = sqlite3.connect('db/nwsl.db')
    cursor = conn.cursor()
    for player in players_data:
        player_id = player.get('player_id', 'Unknown Player ID')
        obj_id = player_id + str(season)
        team_id = player.get('team_id', [])
        general_position = player.get('general_position', 'Unknown General Position')
        minutes_played = player.get('minutes_played', 0)
        shots = player.get('shots', 0)
        shots_on_target = player.get('shots_on_target', 0)
        goals = player.get('goals', 0)
        xgoals = player.get('xgoals', 0)
        xplace = player.get('xplace', 0)
        goals_minus_xgoals = player.get('goals_minus_xgoals', 0)
        key_passes = player.get('key_passes', 0)
        primary_assists = player.get('primary_assists', 0)
        xassists = player.get('xassists', 0)
        primary_assists_minus_xassists = player.get('primary_assists_minus_xassists', 0)
        xgoals_plus_xassists = player.get('xgoals_plus_xassists', 0)
        points_added = player.get('points_added', 0)
        xpoints_added = player.get('xpoints_added', 0)

        if isinstance(team_id, list):
            team_id = team_id[-1]
        elif isinstance(team_id, str):
            pass
        else:
            print('No team associated with player:', player_id)

        cursor.execute('''
            INSERT OR REPLACE INTO player_xgoals (
                id, player_id, team_id, general_position, minutes_played, shots, 
                shots_on_target, goals, xgoals, xplace, goals_minus_xgoals, 
                key_passes, primary_assists, xassists, primary_assists_minus_xassists, 
                xgoals_plus_xassists, points_added, xpoints_added, season
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            obj_id, player_id, team_id, general_position, minutes_played, shots, shots_on_target,
            goals, xgoals, xplace, goals_minus_xgoals, key_passes, primary_assists, xassists,
            primary_assists_minus_xassists, xgoals_plus_xassists, points_added, xpoints_added, int(season)
        ))
        conn.commit()
    conn.close()

def get_player_xgoals(player_id, season):
    print('Fetching player xgoals for:{}, Season: {}'.format(player_id, season))
    obj_id = player_id + str(season)
    conn = sqlite3.connect('db/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM player_xgoals WHERE id = ?', (obj_id,))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    print('Player xgoal returned.')
    return row

def get_all_player_xgoals(season):
    print('Fetching all players xgoals for season: {}'.format(season))
    conn = sqlite3.connect('db/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM player_xgoals WHERE season = ?', (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('All players xgoals returned.')
    return rows
