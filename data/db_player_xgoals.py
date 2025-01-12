from api import make_asa_api_call
import sqlite3

def insert_player_xgoals_by_season(season):
    print('Inserting data for players (xgoal) for season:', season)
    api_string = 'nwsl/players/xgoals?season_name={}&stage_name=Regular Season'.format(str(season))
    players_data = make_asa_api_call(api_string)[1]
    conn = sqlite3.connect('data/nwsl.db')
    cursor = conn.cursor()
    for player in players_data:
        player_id = player.get('player_id', 'Unknown Player ID')
        obj_id = player_id + str(season)
        team_id = player.get('team_id', [])
        general_position = player.get('general_position', 'Unknown General Position')
        minutes_played = player.get('minutes_played', 0)
        shots = player.get('shots', 0)
        shots_on_target = player.get('shots_on_target', 0)
        if shots==0:
            shots_on_target_perc = 0
        else:
            shots_on_target_perc = int((shots_on_target/shots)*100)
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
                shots_on_target, shots_on_target_perc, goals, xgoals, xplace, goals_minus_xgoals, 
                key_passes, primary_assists, xassists, primary_assists_minus_xassists, 
                xgoals_plus_xassists, points_added, xpoints_added, season
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            obj_id, player_id, team_id, general_position, minutes_played, shots, shots_on_target, shots_on_target_perc,
            goals, xgoals, xplace, goals_minus_xgoals, key_passes, primary_assists, xassists,
            primary_assists_minus_xassists, xgoals_plus_xassists, points_added, xpoints_added, int(season)
        ))
        conn.commit()
    conn.close()

def get_player_xgoals(player_id, season):
    print('Fetching player xgoals for:{}, Season: {}'.format(player_id, season))
    obj_id = player_id + str(season)
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = '''
        SELECT 
            px.*,
            pi.*,
            ti.team_name,
            ti.team_abbreviation
            FROM 
                player_xgoals AS px
            JOIN 
                player_info AS pi
            ON 
                px.player_id = pi.player_id
            JOIN
                team_info AS ti
            ON
                px.team_id = ti.team_id   
            WHERE
                px.id = ?;
        '''
    cursor.execute(query, (obj_id,))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    print('Player xgoal returned.')
    return row

def get_all_player_xgoals(season):
    print('Fetching all players xgoals for season: {}'.format(season))
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = '''
        SELECT 
            px.*,
            pi.*,
            ti.team_name
            FROM 
                player_xgoals AS px
            JOIN 
                player_info AS pi
            ON 
                px.player_id = pi.player_id
            JOIN
                team_info AS ti
            ON
                px.team_id = ti.team_id   
            WHERE
                px.season = ?
            ORDER BY
                px.goals;
        '''
    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('All players xgoals returned.')
    return rows

def get_top_player_xgoals_stat(season, sorting_stat, limit):
    print('Players - Fetching top {} sorted by {} for: {}.'.format(limit, sorting_stat, season))
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f'''
        SELECT 
            px.*,
            pi.*,
            ti.*
        FROM 
            player_xgoals AS px
        JOIN 
            player_info AS pi
        ON 
            px.player_id = pi.player_id
        JOIN
            team_info AS ti
        ON
            px.team_id  = ti.team_id
        WHERE
            px.season = ?
        ORDER BY
            px.{sorting_stat} DESC
        LIMIT {limit};
    '''
    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('Top {} sorted by {} for: {} returned'.format(limit, sorting_stat, season))
    return rows

def player_xgoals_get_shots_on_target(season, sorting_stat, limit, shots_condition):
    print('Players - Fetching {} shots on target% sorted by {} for: {}.'.format(limit, sorting_stat, season))
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f'''
        SELECT 
            px.*,
            pi.*,
            ti.*
        FROM 
            player_xgoals AS px
        JOIN 
            player_info AS pi
        ON 
            px.player_id = pi.player_id
        JOIN
            team_info AS ti
        ON
            px.team_id  = ti.team_id
        WHERE
            px.season = ?
            AND px.shots > {shots_condition}
        ORDER BY
            px.{sorting_stat} DESC
        LIMIT {limit};
    '''
    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('Top {} shots on target% sorted by {} for: {} returned'.format(limit, sorting_stat, season))
    return rows

# needs unit test
def player_xgoals_get_minutes_played_defender(season, sorting_stat, limit):
    print('Players - Fetching {} minutes played sorted by {} for: {}.'.format(limit, sorting_stat, season))
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f'''
        SELECT 
            px.*,
            pi.*,
            ti.*
        FROM 
            player_xgoals AS px
        JOIN 
            player_info AS pi
        ON 
            px.player_id = pi.player_id
        JOIN
            team_info AS ti
        ON
            px.team_id  = ti.team_id
        WHERE
            px.season = ?
            AND pi.primary_broad_position == 'DF'
        ORDER BY
            px.{sorting_stat} DESC
        LIMIT {limit};
    '''
    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('Top {} minutes played sorted by {} for: {} returned'.format(limit, sorting_stat, season))
    return rows

# needs unit test
def player_xgoals_get_minutes_played_non_df(season, sorting_stat, limit):
    print('Players - Fetching {} minutes played sorted by {} for: {}.'.format(limit, sorting_stat, season))
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f'''
        SELECT 
            px.*,
            pi.*,
            ti.*
        FROM 
            player_xgoals AS px
        JOIN 
            player_info AS pi
        ON 
            px.player_id = pi.player_id
        JOIN
            team_info AS ti
        ON
            px.team_id  = ti.team_id
        WHERE
            px.season = ?
            AND pi.primary_broad_position != 'DF'
            AND pi.primary_broad_position != 'GK'
        ORDER BY
            px.{sorting_stat} DESC
        LIMIT {limit};
    '''
    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('Top {} minutes played sorted by {} for: {} returned'.format(limit, sorting_stat, season))
    return rows

def get_stat_ranges():
    conn = sqlite3.connect('data/nwsl.db')
    cursor = conn.cursor()
    
    query = """
    SELECT 
        MIN(minutes_played), MAX(minutes_played),
        MIN(shots), MAX(shots),
        MIN(shots_on_target), MAX(shots_on_target),
        MIN(shots_on_target_perc), MAX(shots_on_target_perc),
        MIN(goals), MAX(goals),
        MIN(xgoals), MAX(xgoals),
        MIN(xplace), MAX(xplace),
        MIN(goals_minus_xgoals), MAX(goals_minus_xgoals),
        MIN(key_passes), MAX(key_passes),
        MIN(primary_assists), MAX(primary_assists),
        MIN(xassists), MAX(xassists),
        MIN(primary_assists_minus_xassists), MAX(primary_assists_minus_xassists),
        MIN(xgoals_plus_xassists), MAX(xgoals_plus_xassists),
        MIN(points_added), MAX(points_added),
        MIN(xpoints_added), MAX(xpoints_added)
    FROM player_xgoals;
    """
    
    cursor.execute(query)
    result = cursor.fetchone()
    
    stat_names = [
        "minutes_played", "shots", "shots_on_target", "shots_on_target_perc", 
        "goals", "xgoals", "xplace", "goals_minus_xgoals", 
        "key_passes", "primary_assists", "xassists", 
        "primary_assists_minus_xassists", "xgoals_plus_xassists", 
        "points_added", "xpoints_added"
    ]
    
    stat_ranges = {stat_names[i]: (result[i*2], result[i*2+1]) for i in range(len(stat_names))}
    
    conn.close()
    return stat_ranges

def calculate_player_xgoal_strength(normalized_player_stats):
    weights = {
    "minutes_played": 0.05,
    "shots": 0.1,
    "shots_on_target": 0.1,
    "shots_on_target_perc": 0.05,
    "goals": 0.2,
    "xgoals": 0.15,
    "xplace": 0.05,
    "goals_minus_xgoals": 0.05,
    "key_passes": 0.1,
    "primary_assists": 0.1,
    "xassists": 0.1,
    "primary_assists_minus_xassists": 0.05,
    "xgoals_plus_xassists": 0.1,
    "points_added": 0.1,
    "xpoints_added": 0.05
}
    
    # Calculate weighted score
    player_strength = sum(
    normalized_player_stats[stat] * weights[stat]
    for stat in normalized_player_stats
    if stat not in {'season', 'height_ft', 'height_in'}  # Exclude unwanted keys
    )
    
    return player_strength