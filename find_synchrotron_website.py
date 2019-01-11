"""In their wikipedia URL -> Find website URL and store in DB
1. Access database and pull down first Wikipedia URL.
2. Scrape the Wikipedia page to find website URL of synchrotron
3. Store website URL of synchrotron in database.
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
    '''From https://en.wikipedia.org/wiki/List_of_synchrotron_radiation_facilities
    enter url of synchrotron, and find its website.
    '''
    
#querySelectorAll('div div div div div div div div a')
#https://lightsources.org/lightsources-of-the-world/
    cur.execute('''CREATE TABLE IF NOT EXISTS Websites
        ( name TEXT, external TEXT, lightsource TEXT )
        ''')
    #cur.execute('ALTER TABLE Websites ADD COLUMN lightsource TEXT')
    conn.commit()
    links = cur.fetchall()
    #for link in links:
    #    print('Accessing', link[0])
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
    #try:
    await browser.close();
    cur.execute('''SELECT lightsource FROM Websites''')
    lightsource_url_in_db = cur.fetchall()
    lightsource_url_in_db = ['%s' % x for x in lightsource_url_in_db]
    for i in range(len(forms)):
        if lightsource_url[i] not in lightsource_url_in_db:
            #cur.execute('''INSERT OR IGNORE INTO Websites(lightsource)
            #VALUES (?)''', (lightsource_url[i],))
            browser = await get_browser()
            page = await open_page(browser, lightsource_url[i])
            #print('Scraping', lightsource_url[i], '. .', end = '\r')
            external_element = await page.querySelectorAll('div div div div div div div div a')
            #print('Scraping', lightsource_url[i], '. . .', end = '\r')
            external_header = await page.querySelectorAll('div header h1')
            #print('Scraping', lightsource_url[i], '. . . .', end = '\r')
            external_url = await page.evaluate('(p) => p.href', external_element[0])
            #print('Scraping', lightsource_url[i], '. . . . .', end = '\r')
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
    #except:
    #    print('Connection to website closed: ')

    conn.commit()
    print('Continuing . . .')
    

    #cur.execute('''SELECT * FROM Facilities, Websites INNER JOIN Websites WHERE Websites.name
    #LIKE '%' + Facilities.name + '%' OR Facilities.name LIKE '%' + Websites.name 
    #+ '%' ''')



    #await form.evaluate(form => form.click())
    #elements = await page.content()
    #   data = re.findall('href="(\S+)"',elements)
    #print(data)
    #cleaned_data = []
    #for el in data:
    #    if 'bnl' in el:
    #        cleaned_data.append(el)
#
    #print(len(cleaned_data))
    #print(cleaned_data)

    #infoboxes = await page.querySelectorAll('h2')
    
    #if elements != []:
    #    for element in elements:
    #        info_cell = await page.evaluate('(infobox) => infobox.mw-parser-output', element)
    #        print('\n', info_cell)

async def main():
    conn = sqlite3.connect('pull_data.sqlite')
    cur = conn.cursor()
    browser = await get_browser()
    await extract_website(browser, cur, conn)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(main())
