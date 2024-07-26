from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import time

'''
Content on the NWSL website is dynamically generated. In order to scrape the data, an instance of the page needs to be rendered using Playwright.

Then the soup object can be returned.
'''
def _scrape_dynamic_content(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print('Playwright accessing:', url)
        try:
            page.goto(url)
            page.wait_for_load_state('networkidle')
            page.get_by_role("button", name="Accept All Cookies").click()
            page.locator("div").filter(has_text=re.compile(r"^NWSL x La Liga Summer Cup$")).click()
            page.get_by_text("Regular Season 2024").click()
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
        except:
            print('Failed to navigate to the url:', url)
            print('Verify the url is correct and try again.')
            return 0

'''
The NWSL player page has a table that contains all of the data required for the database.

This function will scrape the site and return a list of lists containing the player data.
'''
def scrape_nwsl_players():
    url = 'https://www.nwslsoccer.com/stats/players/all'
    soup = _scrape_dynamic_content(url)

    # Find the table
    print('Locating player table...')
    table = soup.find('table')

    # Process the table
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
    print('Player data scrapping complete...')
    return data
