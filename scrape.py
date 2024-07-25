from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def _scrape_dynamic_content(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print('Playwright accessing:', url)
        page.goto(url)
        page.wait_for_load_state('networkidle')

        # Get the page content
        html_content = page.content()
        browser.close()

        # Parse with BeautifulSoup
        print('Building HTML content...')
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup

def scrape_nwsl_players():
    url = 'https://www.nwslsoccer.com/stats/players/all'
    soup = _scrape_dynamic_content(url)

    # Find the table
    print('Locating player table...')
    table = soup.find('table')
    tables = soup.find_all('table')

    # Process the table
    data = []
    for table in tables:
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
