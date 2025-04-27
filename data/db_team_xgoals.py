from api import make_asa_api_call
from datetime import datetime, timedelta
import sqlite3
from sklearn.preprocessing import MinMaxScaler
from .data_util import get_db_path

def insert_teams_xgoals_by_season(season):
    print('Inserting teams data (xgoals) for season:', season)
    api_string = f'nwsl/teams/xgoals?season_name={season}&stage_name=Regular Season'
    teams_data = make_asa_api_call(api_string)[1]

    for team in teams_data:
        goals_for = team.get('goals_for', 0)
        xgoals_for = team.get('xgoals_for', 0)
        goals_against = team.get('goals_against', 0)
        points = team.get('points', 0)
        count_games = team.get('count_games', 0)
        predicted_points = round(_calc_predicted_points(count_games, goals_for, goals_against), 3)
        point_diff = round(predicted_points - points, 3)
        goalfor_xgoalfor_diff = round(goals_for - xgoals_for, 3)

        team['predicted_points'] = predicted_points
        team['point_diff'] = point_diff
        team['goalfor_xgoalfor_diff'] = goalfor_xgoalfor_diff

    # Calculate min/max for normalization
    feature_mins, feature_maxs = calculate_feature_min_max(teams_data)

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    for team in teams_data:
        team_id = team.get('team_id', 'Unknown Team ID')
        obj_id = team_id + str(season)
        count_games = team.get('count_games', 0)
        shots_for = team.get('shots_for', 0)
        shots_against = team.get('shots_against', 0)
        goals_for = team.get('goals_for', 0)
        goals_against = team.get('goals_against', 0)
        goal_difference = team.get('goal_difference', 0)
        xgoals_for = round(team.get('xgoals_for', 0), 1)
        xgoals_against = round(team.get('xgoals_against', 0), 1)
        xgoal_difference = round(team.get('xgoal_difference', 0), 1)
        goal_difference_minus_xgoal_difference = round(team.get('goal_difference_minus_xgoal_difference', 0), 1)
        points = team.get('points', 0)
        xpoints = round(team.get('xpoints', 0), 1)
        predicted_points = team['predicted_points']
        point_diff = team['point_diff']
        goalfor_xgoalfor_diff = team['goalfor_xgoalfor_diff']

        # Calculate power score
        team_strength = calculate_team_strength(team, feature_mins, feature_maxs)

        cursor.execute('''
            INSERT OR REPLACE INTO team_xgoals (
                id, team_id, count_games, shots_for, shots_against, goals_for, 
                goals_against, goal_difference, xgoals_for, xgoals_against, 
                xgoal_difference, goal_difference_minus_xgoal_difference, 
                points, xpoints, season, predicted_points, point_diff, goalfor_xgoalfor_diff, team_strength
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            obj_id, team_id, count_games, shots_for, shots_against, goals_for,
            goals_against, goal_difference, xgoals_for, xgoals_against,
            xgoal_difference, goal_difference_minus_xgoal_difference,
            points, xpoints, int(season), predicted_points, point_diff, goalfor_xgoalfor_diff, team_strength
        ))

        conn.commit()
    conn.close()


def get_top_team_xgoals_stat(season, sorting_stat):
    print('Teams - Xgoals in {} for: {}.'.format(sorting_stat, season))
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f'''
        SELECT 
            tx.*,
            ti.*
        FROM 
            team_xgoals AS tx
        JOIN 
            team_info AS ti
        ON 
            tx.team_id = ti.team_id
        WHERE
            tx.season = ?
        ORDER BY
            tx.{sorting_stat} DESC;
    '''
    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('Team XGoals sorted by {} for: {} returned'.format(sorting_stat, season))
    return rows

def get_team_xgoals_by_season(team_id, season):
    print('Teams - Xgoals in {} for: {}.'.format(team_id, season))
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f'''
        SELECT 
            tx.*,
            ti.*
        FROM 
            team_xgoals AS tx
        JOIN 
            team_info AS ti
        ON 
            tx.team_id = ti.team_id
        WHERE
            tx.season = ? AND tx.team_id = ?;
    '''
    cursor.execute(query, (season, team_id))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('Team XGoals sorted by {} for: {} returned'.format(team_id, season))
    return rows

def _calc_predicted_points(count_games, goals_for, goals_against):
    perc_points_prediction = (goals_for**1.35)/((goals_for**1.35) + (goals_against**1.35))
    available_points = count_games * 3
    predicted_points = perc_points_prediction * available_points
    return(predicted_points)

def calculate_feature_min_max(teams_data):
    keys = [
        'xgoal_difference',
        'goal_difference',
        'xpoints',
        'points',
        'goal_difference_minus_xgoal_difference',
        'goalfor_xgoalfor_diff'
    ]
    feature_mins = {key: float('inf') for key in keys}
    feature_maxs = {key: float('-inf') for key in keys}
    
    for team in teams_data:
        for key in keys:
            val = team.get(key, 0)
            if val < feature_mins[key]:
                feature_mins[key] = val
            if val > feature_maxs[key]:
                feature_maxs[key] = val
    return feature_mins, feature_maxs

def calculate_team_strength(team, feature_mins, feature_maxs):
    features = {
        'xgoal_difference': team.get('xgoal_difference', 0),
        'goal_difference': team.get('goal_difference', 0),
        'xpoints': team.get('xpoints', 0),
        'points': team.get('points', 0),
        'goal_difference_minus_xgoal_difference': team.get('goal_difference_minus_xgoal_difference', 0),
        'goalfor_xgoalfor_diff': team.get('goalfor_xgoalfor_diff', 0)
    }

    normalized = {}
    for key in features:
        min_val = feature_mins[key]
        max_val = feature_maxs[key]
        val = features[key]
        base_normalized = (val - min_val) / (max_val - min_val) if max_val != min_val else 0.5

        if key == 'goalfor_xgoalfor_diff':
            normalized[key] = adjust_goalfor_xgoalfor_diff(val)
        else:
            normalized[key] = base_normalized

    team_strength = (
        0.333 * normalized['xgoal_difference'] +
        0.222 * normalized['goal_difference'] +
        0.167 * normalized['xpoints'] +
        0.111 * normalized['points'] +
        0.111 * normalized['goal_difference_minus_xgoal_difference'] +
        0.056 * normalized['goalfor_xgoalfor_diff']
    )
    
    return round(team_strength * 100, 1)

def insert_team_strength_history(season):
    print(f"Checking team strength update needs for season {season}...")
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if not season:
        print("No season value provided.")
        return

    # Get strength data for the season
    rows = get_team_strength_for_season(cursor, season)
    if not rows:
        print(f"No team strength data found for season {season}.")
        return

    # Check which teams need an update by comparing count_games
    teams_to_update = []
    for row in rows:
        team_id = row['team_id']
        cursor.execute('''
            SELECT count_games, team_strength FROM team_strength_history
            WHERE season = ? AND team_id = ?
            ORDER BY count_games DESC
            LIMIT 1
        ''', (season, team_id))
        existing = cursor.fetchone()

        if existing is None:
            teams_to_update.append(row)
        elif row['count_games'] > existing['count_games']:
            teams_to_update.append(row)
        elif row['count_games'] == existing['count_games'] and abs(row['team_strength'] - existing['team_strength']) > 0.001:
            teams_to_update.append(row)

    if not teams_to_update:
        print(f"No updates needed for season {season}.")
        return

    # Sort by strength and insert updated values
    sorted_rows = sorted(teams_to_update, key=lambda r: r['team_strength'], reverse=True)
    today = datetime.now().strftime('%Y-%m-%d')

    for rank, row in enumerate(sorted_rows, start=1):
        # Check if same count_games exists
        cursor.execute('''
            SELECT 1 FROM team_strength_history
            WHERE team_id = ? AND season = ? AND count_games = ?
        ''', (row['team_id'], season, row['count_games']))
        exists = cursor.fetchone()

        if exists:
            # Update existing record
            cursor.execute('''
                UPDATE team_strength_history
                SET team_strength = ?, team_rank = ?, date_stamp = ?
                WHERE team_id = ? AND season = ? AND count_games = ?
            ''', (
                row['team_strength'],
                rank,
                today,
                row['team_id'],
                season,
                row['count_games']
            ))
        else:
            # Insert new record
            cursor.execute('''
                INSERT INTO team_strength_history (
                    team_id,
                    season,
                    team_strength,
                    team_rank,
                    date_stamp,
                    count_games
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                row['team_id'],
                season,
                row['team_strength'],
                rank,
                today,
                row['count_games']
            ))

    conn.commit()
    conn.close()
    print(f"Updated {len(teams_to_update)} teams for season {season}.")
    print(f"Updated these teams: {teams_to_update}")


def get_team_strength_for_season(cursor, season):
    cursor.execute('''
        SELECT team_id, team_strength, count_games 
        FROM team_xgoals 
        WHERE season = ?;
    ''', (season,))
    return cursor.fetchall()

def get_team_strength_by_season(season):
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 
            tsh.*,
            ti.*
        FROM 
            team_strength_history AS tsh
        JOIN 
            team_info AS ti
        ON 
            tsh.team_id = ti.team_id
        WHERE 
            tsh.season = ?
        ORDER BY 
            tsh.count_games DESC,
            tsh.team_rank ASC;
    ''', (season,))
    
    rows = cursor.fetchall()
    conn.close()
    return rows

def adjust_goalfor_xgoalfor_diff(value):
    if value >= 0:
        # Reward positive overperformance with a slight boost
        return min(1.0, 0.6 + 0.4 * value)  # Caps at 1.0
    else:
        # Penalize underperformance but less harshly
        return max(0.0, 0.5 + value)  # Doesn't drop too far
