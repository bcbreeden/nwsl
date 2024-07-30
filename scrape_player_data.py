from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import time
import pandas as pd

'''
Content on the NWSL website is dynamically generated. In order to scrape the data, an instance of the page needs to be rendered using Playwright.

Then the soup object can be returned.
'''
def _scrape_dynamic_player_content(url, season):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print('Playwright accessing:', url)
        try:
            page.goto(url)
            page.wait_for_load_state('networkidle')
            page.get_by_role("button", name="Accept All Cookies").click()
            listbox_div = page.locator('[role="listbox"]').first
            listbox_div.click()
            page.get_by_text(season).click()
            # The NWSL page uses React and it needs a few seconds to load.
            print('React components loading...')
            time.sleep(5)

            # Get the page content
            html_content = page.content()
            browser.close()

            # Parse with BeautifulSoup
            print('Building HTML content...')
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup
        except Exception as e:
            print(f"An error occurred: {e}")
            print('Debugging URL:', url)
            print('Debugging Season:', season)
            print('Verify the url and season is correct and try again.')
            return 0

def _get_player_first_last_names(table):
    name_data = []
    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        cell_data = []
        for cell in cells:
            first_name = cell.find('span', class_='d3w-player-name--first')
            last_name = cell.find('span', class_='d3w-player-name--last')
            if first_name and last_name:
                cell_data.append(first_name.get_text(strip=True))
                cell_data.append(last_name.get_text(strip=True))
                name_data.append(cell_data)
                break
            if not first_name and last_name:
                cell_data.append(last_name.get_text(strip=True))
                cell_data.append(None)
                name_data.append(cell_data)
                break
    df = pd.DataFrame(name_data, columns=['First Name', 'Last Name'])
    return(df)

def _get_player_data(table):
    data = []
    rows = table.find_all('tr')
    headers_needed = True
    for row in rows:
        cells = row.find_all(['td', 'th'])
        cell_data = [cell.get_text(strip=True) for cell in cells]
        try:
            image_tag = cells[0].find('img')
            cell_data[0] = image_tag.get('alt', '')
        except:
            if headers_needed:
                data.append(cell_data)
                headers_needed = False
        data.append(cell_data)
        data_header = data[0]
    rows = data[1:]

    # The scraping function grab an a11y row that duplicates the header and the first row. This will seek to remove the duplicate.
    if rows[0] == data_header:
        rows = rows[1:]
    
    df = pd.DataFrame(rows, columns=data_header)

    # If there is a blank column (usually due to an icon or other feature in the site data), we can remove it.
    df = df.loc[:, df.columns != '']
    return df


'''
The NWSL player page has a table that contains all of the data required for the database.

This function will scrape the site and return a list of lists containing the player data.
'''
def scrape_nwsl_players(season):
    url = 'https://www.nwslsoccer.com/stats/players/all'
    soup = _scrape_dynamic_player_content(url, season)

    if soup == 0:
        return soup
    else:
        # Find the table
        print('Locating player table...')
        table = soup.find('table')
        names_df = _get_player_first_last_names(table)
        data_df = _get_player_data(table)
        full_data = pd.concat([names_df, data_df], axis=1)

        print('Player data scrapping complete...')
        return full_data