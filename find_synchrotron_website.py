"""1. Go onto lightsources.org.
2. Scrape page containing links to subdomains for synchrotrons.
3. Enter each synchrotron page and extract name and website.
4. Store name and website in local database.

Can be run to update database if additional synchrotrons have been 
added to the website.
"""

__all__ = []
__version__ = '0.1'
__author__ = 'Richard Skogeby'

import sqlite3
import re
from time import sleep

import asyncio
from pyppeteer import launch

from pull_data import *
from stopwatch import *


async def extract_website(browser, cur, conn):
    '''From https://lightsources.org/lightsources-of-the-world/
    go into each synchrotron, extract its name and website and store 
    in local database.
    '''
    
    cur.execute('''CREATE TABLE IF NOT EXISTS Websites
        ( name TEXT, external TEXT, lightsource TEXT )
        ''')
    conn.commit()
    links = cur.fetchall()
    page = await open_page(browser, 'https://lightsources.org/lightsources-of-the-world/')
    forms = []
    itr = 1
    while True:
        xpath = ''.join(['//*[@id="post-204"]/div/div/div[2]/div[', str(itr), ']/a'])
        itr = itr + 1
        forms.append(await page.xpath(xpath));
        if len(forms[len(forms)-1]) == 0:
            forms.pop()
            break
    
    lightsource_url = []
    i = 0
    for form in forms:
        lightsource_url.append(await page.evaluate('(p) => p.href', form[0]))
    await browser.close();
    cur.execute('''SELECT lightsource FROM Websites''')
    lightsource_url_in_db = cur.fetchall()
    lightsource_url_in_db = ['%s' % x for x in lightsource_url_in_db]
    for i in range(len(forms)):
        if lightsource_url[i] not in lightsource_url_in_db:
            browser = await get_browser()
            page = await open_page(browser, lightsource_url[i])
            external_element = await page.querySelectorAll('div div div div div div div div a')
            external_header = await page.querySelectorAll('div header h1')
            external_url = await page.evaluate('(p) => p.href', external_element[0])
            external_facilities = await page.evaluate('(p) => p.innerText', external_header[0])
            cur.execute('''INSERT OR IGNORE INTO Websites(name,external,lightsource)
            VALUES (?,?,?)''', (external_facilities,external_url,lightsource_url[i]))
            print(lightsource_url[i], 'scraped.')
            conn.commit()
            await browser.close();
        else:
            cur.execute('''SELECT name FROM Websites WHERE lightsource == (?)''', (lightsource_url[i],))
            name_in_db = cur.fetchone()
            print('Website for:', name_in_db[0], 'is already in the database.')


async def main():
    conn = sqlite3.connect('pull_data.sqlite')
    cur = conn.cursor()
    browser = await get_browser()
    await extract_website(browser, cur, conn)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(main())
