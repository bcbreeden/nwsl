import pandas as pd

from scrape import scrape_nwsl_players

def format_player_data_for_db():
    data = scrape_nwsl_players()
    data_header = data[0]
    rows = data[1:]

    # The scraping function grab an a11y row that duplicates the header and the first row. This will seek to remove the duplicate.
    if rows[0] == data_header:
        rows = rows[1:]
    
    df = pd.DataFrame(rows, columns=data_header)

    # If there is a blank column (usually due to an icon or other feature in the site data), we can remove it.
    df = df.loc[:, df.columns != '']
