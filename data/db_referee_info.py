from api import make_asa_api_call
from .data_util import get_db_path
import sqlite3

def insert_all_referee_info():
    print('Attempting to insert all referee info...')
    referees_data = make_asa_api_call('nwsl/referees')[1]
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    for referee in referees_data:
        referee_id = referee.get('referee_id', 'Unknown ID')
        referee_name = referee.get('referee_name', 'Unknown Name')
        nationality = referee.get('nationality', 'Unknown Nationality')

        cursor.execute('''
            INSERT OR REPLACE INTO referee_info (
                referee_id,
                referee_name,
                nationality
            ) VALUES (?, ?, ?)
        ''', (referee_id, referee_name, nationality))
        conn.commit()

    conn.close()
    print('All referee info successfully entered into the database.')

def get_referee_by_id(referee_id):
    print('Attempting to get referee info by ID:', referee_id)
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM referee_info WHERE referee_id = ?
    ''', (referee_id,))
    
    row = cursor.fetchone()
    conn.commit()
    conn.close()

    if row:
        print('Referee info successfully retrieved:', referee_id)
    else:
        print('No referee found for ID:', referee_id)

    return row
