from db import db_setup, db_player_info, db_team_info

if __name__ == "__main__":
    db_setup.create_tables()
    db_player_info.insert_all_players_info()
    db_team_info.insert_team_info()