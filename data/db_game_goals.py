from .data_util import get_db_path
import sqlite3
from .db_game_shots import get_shots_by_game_id

def insert_game_goals_by_game_id(game_id):
    print(f"Inserting goal shots for game {game_id}")
    game_shot_data = get_shots_by_game_id(game_id)
    
    if not game_shot_data:
        print(f"No shot data found for game {game_id}")
        return

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    for shot in game_shot_data:
        if shot["goal"] == 1:
            shooter_id = shot["shooter_player_id"]
            assist_id = shot["assist_player_id"]
            team_id = shot["team_id"]
            expanded_minute = shot["expanded_minute"]
            pattern_of_play = shot["pattern_of_play"]

            cursor.execute('''
                INSERT OR IGNORE INTO game_goals (
                    game_id, shooter_player_id, assist_player_id, 
                    team_id, expanded_minute, pattern_of_play
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                game_id, shooter_id, assist_id, 
                team_id, expanded_minute, pattern_of_play
            ))
            conn.commit()
    cursor.close()
    conn.close()

def get_goals_by_game_id(game_id):
    print('Fetching goal records for game id:', game_id)
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM game_goals 
        WHERE game_id = ? 
        ORDER BY expanded_minute
    ''', (game_id,))
    rows = cursor.fetchall()
    conn.close()
    print(f'{len(rows)} goal(s) returned.')
    return rows
