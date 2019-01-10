""" Create and fill a database pull_data.sqlite with the Wikipedia list of
synchrotrons in the world. In addition to the synchrotron name the Wikipedia 
website address of the synchrotrons, its location, country, energy, circumference,
year of commissioning and year of decommissioning are recorded.
"""

__all__ = ['get_browser', 'open_page', 'insert_wikipedia_table_into_db']
__version__ = '1.0'
__author__ = 'Richard Skogeby'

import sqlite3
import asyncio
from time import time, sleep
from pyppeteer import launch

def formatted_time(t):
    r_n = 3
    if t <= 1e-3:
        t = t * 1e6
        t_string = ''.join([str(round(t,r_n)),' us'])
        return t_string 
    if t <= 1e-0:
        t = t * 1e3
        t_string = ''.join([str(round(t,r_n)),' ms'])
        return t_string
    if t <= 999:
        t = t * 1e0
        t_string = ''.join([str(round(t,r_n)),' s'])
        return t_string
    else:
        return ''.join([str(t),' s'])

def timer(function):
    def f(*args, **kwargs):
        before = time()
        print('Running', function.__name__, '. . .', end='\r')
        rv = function(*args, **kwargs)
        after = time()
        t = after - before
        print(function.__name__, 'executed in', formatted_time(t))
        return rv
    return f

@timer
async def get_browser():
    return await launch(headless=True)

@timer
async def open_page(browser, url):
    page = await browser.newPage()
    await page.goto(url)
    return page

@timer
def create_db():
    conn = sqlite3.connect('pull_data.sqlite')
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS Facilities')
    cur.execute('''CREATE TABLE Facilities
        (name TEXT, wikipedia TEXT, location TEXT, country TEXT, 
        energy REAL, circumference REAL, commissioned INTEGER, decommissioned INTEGER)
    ''')
    conn.commit()
    return conn, cur

@timer
async def insert_wikipedia_table_into_db(browser, conn, cur):
    # Access page and query urls in the table as well as content of each cell
    base_url = 'https://en.wikipedia.org/wiki/List_of_synchrotron_radiation_facilities'
    page = await open_page(browser, base_url)
    elements = await page.querySelectorAll('div table tbody tr td a')
    cells = await page.querySelectorAll('div table tbody tr td')
    it = 0  # Iterate row_length
    els = 0  # Iterate website
    row_length = 7
    row = []
    for cell in cells:
        # Save the table content cell by cell. Note! It excludes the header.
        wiki_cell = await page.evaluate('(element) => element.textContent', cell)

        # Get rid of newline characters.
        if '\n' in wiki_cell:
            wiki_cell = wiki_cell.replace('\n', '')

        # Build row
        row.append(wiki_cell)
        if it == 0:
            facility_url = await page.evaluate('(element) => element.href', elements[els])
            row.append(facility_url)

        # Insert into database
        if it == row_length-1:
            cur.execute('''INSERT OR IGNORE INTO Facilities(name,wikipedia,
            location,country,energy,circumference,commissioned,decommissioned) 
            VALUES (?,?,?,?,?,?,?,?)''', tuple(row))
            row = []
            conn.commit()
            it = 0
        else:
            it = it + 1            


async def main():
    conn, cur = create_db()
    browser = await get_browser()
    await insert_wikipedia_table_into_db(browser, conn, cur)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(main())
