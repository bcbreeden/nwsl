from api import make_asa_api_call
from .data_util import get_db_path
import sqlite3

def insert_all_stadium_info():
    print('Attempting to insert all stadium info...')
    stadia_data = make_asa_api_call('nwsl/stadia')[1]
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    for stadium in stadia_data:
        stadium_id = stadium.get('stadium_id', 'Unknown ID')
        stadium_name = stadium.get('stadium_name', 'Unknown Name')
        capacity = stadium.get('capacity', -1)
        year_built = stadium.get('year_built', -1)
        roof = stadium.get('roof', False)
        turf = stadium.get('turf', False)
        street = stadium.get('street', 'Unknown Street')
        city = stadium.get('city', 'Unknown City')
        province = stadium.get('province', 'Unknown Province')
        country = stadium.get('country', 'Unknown Country')
        postal_code = stadium.get('postal_code', 'Unknown Postal')
        latitude = stadium.get('latitude', 0.0)
        longitude = stadium.get('longitude', 0.0)
        field_x = stadium.get('field_x', -1)
        field_y = stadium.get('field_y', -1)

        cursor.execute('''
            INSERT OR REPLACE INTO stadium_info (
                stadium_id,
                stadium_name,
                capacity,
                year_built,
                roof,
                turf,
                street,
                city,
                province,
                country,
                postal_code,
                latitude,
                longitude,
                field_x,
                field_y
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            stadium_id, stadium_name, capacity, year_built, roof, turf,
            street, city, province, country, postal_code,
            latitude, longitude, field_x, field_y
        ))
        conn.commit()

    conn.close()
    print('All stadium info successfully entered into the database.')


def get_stadium_by_id(stadium_id):
    print('Attempting to get stadium info by ID:', stadium_id)
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM stadium_info WHERE stadium_id = ?
    ''', (stadium_id,))
    
    row = cursor.fetchone()
    conn.close()

    if row:
        print('Stadium info successfully retrieved:', stadium_id)
    else:
        print('No stadium found for ID:', stadium_id)

    return row
