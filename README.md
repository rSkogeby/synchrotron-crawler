# Synchrotron Crawler
Pulling data of which detectors are used from all beamlines of all 
   synchrotrons of interest.
   
    1. Access https://en.wikipedia.org/wiki/List_of_synchrotron_radiation_facilities
    2. Save all Facility names and corresponding wikipedia URLs in a DB
    3. In their wikipedia URL -> Find website URL and store in DB
    4. Access website URL and look for link to Beamlines
    5. Find links to all beamlines and store in DB
    6. For each beamline find detectors used
    7. Categorise detectors, clean up to account for various naming conventions etc.
    8. Visualise

Install required modules:
```bash
pip install -r requirements.txt
```

