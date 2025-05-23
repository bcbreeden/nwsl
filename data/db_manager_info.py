from api import make_asa_api_call
from .data_util import get_db_path
import sqlite3

def insert_all_manager_info():
    print('Attempting to insert all managers info...')
    managers_data = make_asa_api_call('nwsl/managers')[1]
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    for manager in managers_data:
        manager_id = manager.get('manager_id', 'Unknown ID')
        manager_name = manager.get('manager_name', 'Unknown Name')
        nationality = manager.get('nationality', 'Unknown Nationality')

        cursor.execute('''
            INSERT OR REPLACE INTO manager_info (
                manager_id,
                manager_name,
                nationality
            ) VALUES (?, ?, ?)
        ''', (manager_id, manager_name, nationality))
        conn.commit()
    conn.close()
    print('All managers info successfully entered into the database.')

def get_manager_by_id(manager_id):
    print('Attempting to get manager info by ID:', manager_id)
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM manager_info WHERE manager_id = ?
    ''', (manager_id,))
    
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    print('Manager info successfully retrieved from the database:', manager_id)
    return row