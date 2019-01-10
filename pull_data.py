import sqlite3
import pprint
import asyncio
from pyppeteer import launch


async def get_browser():
    return await launch(headless = True)

async def open_page(browser, url):
    page = await browser.newPage()
    await page.goto(url)
    return page

async def extract_facility(browser, url):
    # Database 
    conn = sqlite3.connect('content.sqlite')
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS Facilities')
    cur.execute('''CREATE TABLE Facilities
        (name TEXT, wikipedia TEXT, location TEXT, country TEXT, 
        energy REAL, circumference REAL, commissioned INTEGER, decommissioned INTEGER)
    ''')
    conn.commit()

    page = await open_page(browser,url)
    elements = await page.querySelectorAll('div table tbody tr td a')
    cells = await page.querySelectorAll('div table tbody tr td')
    stop = 0
    it = 0
    els = 0
    table_rows = ['name','location','country','energy','circumference','commissioned','decommissioned']
    print(len(cells))
    row_length = 7
    row = []
    for cell in cells:
        wiki_cell = await page.evaluate('(element) => element.textContent', cell)
        
        if '\n' in wiki_cell:
            wiki_cell = wiki_cell.replace('\n','')  
        
        # Build row        
        row.append(wiki_cell)
        if it == 0:
            facility_url = await page.evaluate('(element) => element.href', elements[els])
            row.append(facility_url)       

        # Insert into DB   
        if it == row_length-1:
            cur.execute('''INSERT OR IGNORE INTO Facilities(name,wikipedia,location,country,
            energy,circumference,commissioned,decommissioned) VALUES ( ?,?,?,?,?,
            ?,?,? )''', tuple(row))
            row = []
            conn.commit()
            it = 0
        else:
            it = it + 1

    #it = 2
    #row_length = 7
    #facility_countries = []
    #while (it + row_length <= len(countries)):
    #    facility_countries.append(countries[it])
    #    it = it + row_length
    #facility_dict = {}
    #it = 0
    #for element in elements:
    #    facility_name = await page.evaluate('(element) => element.textContent', element)
    #    facility_url = await page.evaluate('(element) => element.href', element)
    #    facility_country = facility_countries[it]
    #    it = it + 1
    #    if facility_name not in facility_dict:
    #        print("Inserting", facility_name,"into database.")
    #        #cur.execute('''INSERT INTO Facilities (name, website, country) 
    #        #                            VALUES (?,?,?)''',
    #        #                            (facility_name,
    #        #                            facility_url,
    #        #                            facility_country)
    #        #                            )
    #        facility_dict[facility_name] = facility_url 
    #        
    #conn.commit()
    return {}


async def main():

    base_url = 'https://en.wikipedia.org/wiki/List_of_synchrotron_radiation_facilities'
    browser = await get_browser()
    facility_dict = await extract_facility(browser,base_url)
    print(facility_dict)
    print('_____________')
    print()
    pprint.pprint(facility_dict)



if __name__ == '__main__':
    
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(main())

    """Pulling data of which detectors are used from all beamlines of all 
   synchrotrons of interest.
   
    1. Access https://en.wikipedia.org/wiki/List_of_synchrotron_radiation_facilities
    2. Save all Facility names and corresponding wikipedia URLs in a DB
    3. In their wikipedia URL -> Find website URL and store in DB
    4. Access website URL and look for link to Beamlines
    5. Find links to all beamlines and store in DB
    6. For each beamline find detectors used
    7. Categorise detectors, clean up to account for various naming conventions etc.
    8. Visualise
    """

    # Ignore SSL certificate errors
    # Set verify = False
    #ctx = ssl.create_default_context()
    #ctx.check_hostname = False
    #ctx.verify_mode = ssl.CERT_NONE
    #url = 'https://en.wikipedia.org/wiki/List_of_synchrotron_radiation_facilities'
    #with urllib.request.urlopen(url, context = ctx ) as response:
    #    html = response.read()
    #    print(html)

