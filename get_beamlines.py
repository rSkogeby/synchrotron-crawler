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


async def get_beamlines(browser, cur, conn):
    cur.execute('''SELECT external FROM Websites''')
    websites = cur.fetchall()
    websites = ['%s' % x for x in websites]
    website = websites[0]
    page = await open_page(browser, website)
    


    


async def main():
    conn = sqlite3.connect('pull_data.sqlite')
    cur = conn.cursor()
    browser = await get_browser()
    await get_beamlines(browser, cur, conn)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(main())
