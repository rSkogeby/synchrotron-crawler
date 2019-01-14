"""Access website URL and look for link to Beamlines
"""

__all__ = []
__version__ = '0.1'
__author__ = 'Richard Skogeby'

import sqlite3
from time import sleep

import asyncio
from pyppeteer import launch

from find_synchrotron_website import *
from pull_data import *
from stopwatch import *

def create_table(conn, cur):
    cur.execute('''CREATE TABLE IF NOT EXISTS Beamlines
        ( website TEXT, beamline_subdomain TEXT)
        ''')
    conn.commit()
    return 

def escape_xpath_string(search_string):
    split_quotes = search_string.replace('\'','')
    return ''.join(split_quotes)


async def click_by_text(browser, page, search_string, website):
    escaped_text = escape_xpath_string(search_string)
    link_handlers = await page.Jx('//a[contains(text(), %s)]' % escaped_text)

    if len(link_handlers) > 0:
        for link_handler in link_handlers:         
            print(link_handlers[0])
            wiki_cell = await page.evaluate('(element) => element.href', link_handler)
            if website in wiki_cell:
                print('First if:', wiki_cell)
                if 'eamline' in wiki_cell:
                    print('Second if:', wiki_cell)
                    await browser.close()
                    browser = await get_browser()
                    page = await open_page(browser, wiki_cell)
                    break
                continue
            else:
                continue
            #await page.click(link_handlers[0])
            #await asyncio.wait([page.click(link_handlers[0]), page.waitForNavigation()])
    else:
        print('Beamlines section not found on', website, ' ... Continuing.') 


async def get_beamlines(browser, cur, conn):
    cur.execute('''SELECT external FROM Websites''')
    websites = cur.fetchall()
    websites = ['%s' % x for x in websites]
    n_websites_accessed = 0
    total_n_websites = len(websites)
    for website in websites:
        print('Parsing', n_websites_accessed, '/', total_n_websites, ':', website)
        page = await open_page(browser, website)
        search_string = 'Beamlines'
        await click_by_text(browser, page, search_string, website)
        n_websites_accessed = n_websites_accessed + 1
   


async def main():
    conn = sqlite3.connect('pull_data.sqlite')
    cur = conn.cursor()
    browser = await get_browser()
    await get_beamlines(browser, cur, conn)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(main())
