"""1. Go onto lightsources.org.
2. Scrape page containing links to subdomains for synchrotrons.
3. Enter each synchrotron page and extract name and website.
4. Store name and website in local database.

Can be run to update database if additional synchrotrons have been 
added to the website.
"""

__all__ = ['extract_website']
__version__ = '1.0'
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
    #Enter table into open database.
    cur.execute('''CREATE TABLE IF NOT EXISTS Websites
        ( name TEXT, external TEXT, lightsource TEXT )
        ''')
    conn.commit()

    #Open lightsource.org and process xpaths subdomains with synchrotrons
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
    
    #Using xpath evaluate page to extract url (href)
    lightsource_url = []
    i = 0
    for form in forms:
        lightsource_url.append(await page.evaluate('(p) => p.href', form[0]))
    await browser.close();

    #Check if subdomain urls (e.g. lightsources.org/.../diamond-light-source) exist
    cur.execute('''SELECT lightsource FROM Websites''')
    its_database_cell = cur.fetchall()
    its_database_cell = ['%s' % x for x in its_database_cell] #Turn list of tuples into list of strings
    for i in range(len(forms)):
        if lightsource_url[i] not in its_database_cell: #Do the check mentioned two comments up           
            #Open page and extract website
            browser = await get_browser() #Open new browser for every subdomain. Avoids browser timeout error. 
            page = await open_page(browser, lightsource_url[i])
            external_website_element = await page.querySelectorAll('div div div div div div div div a')
            synchrotron_name_element = await page.querySelectorAll('div header h1')
            external_website = await page.evaluate('(p) => p.href', external_website_element[0])
            synchrotron_name = await page.evaluate('(p) => p.innerText', synchrotron_name_element[0])
            cur.execute('''INSERT OR IGNORE INTO Websites(name,external,lightsource)
            VALUES (?,?,?)''', (synchrotron_name,external_website,lightsource_url[i]))
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
