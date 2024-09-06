from api import make_asa_api_call
import sqlite3

def insert_teams_xgoals_by_season(season):
    print('Inserting teams data (xgoals) for season:', season)
    api_string = 'nwsl/teams/xgoals?season_name={}&stage_name=Regular Season'.format(str(season))
    teams_data = make_asa_api_call(api_string)[1]
    conn = sqlite3.connect('db/nwsl.db')
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
        xgoals_for = team.get('xgoals_for', 0)
        xgoals_against = team.get('xgoals_against', 0)
        xgoal_difference = team.get('xgoal_difference', 0)
        goal_difference_minus_xgoal_difference = team.get('goal_difference_minus_xgoal_difference', 0)
        points = team.get('points', 0)
        xpoints = team.get('xpoints', 0)

        cursor.execute('''
            INSERT OR REPLACE INTO team_xgoals (
                id, team_id, count_games, shots_for, shots_against, goals_for, 
                goals_against, goal_difference, xgoals_for, xgoals_against, 
                xgoal_difference, goal_difference_minus_xgoal_difference, 
                points, xpoints, season
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                obj_id, team_id, count_games, shots_for, shots_against, goals_for,
                goals_against, goal_difference, xgoals_for, xgoals_against,
                xgoal_difference, goal_difference_minus_xgoal_difference,
                points, xpoints, int(season)
            ))
        conn.commit()
    conn.close()

def get_top_team_xgoals_stat(season, sorting_stat):
    print('Teams - Xgoals in {} for: {}.'.format(sorting_stat, season))
    conn = sqlite3.connect('db/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f'''
        SELECT 
            tx.*,
            ti.team_name
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