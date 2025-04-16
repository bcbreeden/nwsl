from api import make_asa_api_call
import sqlite3
from sklearn.preprocessing import MinMaxScaler

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

    conn = sqlite3.connect('data/nwsl.db')
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
        xpoints = team.get('xpoints', 0)
        predicted_points = team['predicted_points']
        point_diff = team['point_diff']
        goalfor_xgoalfor_diff = team['goalfor_xgoalfor_diff']

        # Calculate power score
        power_score = calculate_power_score(team, feature_mins, feature_maxs)

        cursor.execute('''
            INSERT OR REPLACE INTO team_xgoals (
                id, team_id, count_games, shots_for, shots_against, goals_for, 
                goals_against, goal_difference, xgoals_for, xgoals_against, 
                xgoal_difference, goal_difference_minus_xgoal_difference, 
                points, xpoints, season, predicted_points, point_diff, goalfor_xgoalfor_diff, power_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            obj_id, team_id, count_games, shots_for, shots_against, goals_for,
            goals_against, goal_difference, xgoals_for, xgoals_against,
            xgoal_difference, goal_difference_minus_xgoal_difference,
            points, xpoints, int(season), predicted_points, point_diff, goalfor_xgoalfor_diff, power_score
        ))

        conn.commit()
    conn.close()


def get_top_team_xgoals_stat(season, sorting_stat):
    print('Teams - Xgoals in {} for: {}.'.format(sorting_stat, season))
    conn = sqlite3.connect('data/nwsl.db')
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
        'point_diff',
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

def calculate_power_score(team, feature_mins, feature_maxs):
    features = {
        'xgoal_difference': team.get('xgoal_difference', 0),
        'goal_difference': team.get('goal_difference', 0),
        'xpoints': team.get('xpoints', 0),
        'points': team.get('points', 0),
        'goal_difference_minus_xgoal_difference': team.get('goal_difference_minus_xgoal_difference', 0),
        'point_diff': team.get('point_diff', 0),
        'goalfor_xgoalfor_diff': team.get('goalfor_xgoalfor_diff', 0)
    }

    normalized = {}
    for key in features:
        min_val = feature_mins[key]
        max_val = feature_maxs[key]
        val = features[key]
        normalized[key] = (val - min_val) / (max_val - min_val) if max_val != min_val else 0.5

    power_score = (
        0.30 * normalized['xgoal_difference'] +
        0.20 * normalized['goal_difference'] +
        0.15 * normalized['xpoints'] +
        0.10 * normalized['points'] +
        0.10 * normalized['goal_difference_minus_xgoal_difference'] +
        0.10 * normalized['point_diff'] +
        0.05 * normalized['goalfor_xgoalfor_diff']
    )
    
    return round(power_score * 100, 1)
