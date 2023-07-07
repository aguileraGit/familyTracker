# More to do

- [ ] Add board game to board game DB!
- [ ] Update profile to be nicer (add photos)
- [ ] Look at summary section below
 - [ ] Look at web alerts to send notifications (report is ready or reminder to do push ups)
- [ ] Add users to make public (requires server)
- Add point per birthday (script that runs daily)
- Calendar(s)


https://pythonbasics.org/flask-login/
https://stackoverflow.com/questions/45701726/pandas-dataframe-to-bootstrap-table
https://plotly.com/python/templates/
https://blog.heptanalytics.com/flask-plotly-dashboard/


### BiWeekly Summary:
Clicking on (more) could lead to analytics page
 - Who scored the most points this week?
 - How many flies were killed?
 - Did Diego do any push ups?
 - What games were played?

### Analytics Page
By User:
 - Points per DB Table (pie graph): Fly/Board Games/Chia Seeds/Misc
 - Misc reasons for points
 
By Family:
 -  Number of games played
 - Total number of flies killed



# Configuration
Flask App pulls configuration from config.py. This file is not pushed to Github.

## Example file (`config.py`)
```
TESTING = True
DEBUG = True
FLASK_ENV = 'development'
SECRET_KEY = 'someSuperKey01234'
DBHOST = 'dbHostName'
DBNAME = 'familyCounts'
```

## Service
```
[Unit]
Description=AguileraTracker

[Service]
ExecStart=flask run -h 192.168.1.105 -p 8585
User=pi
WorkingDirectory=/home/pi/Projects/familyTracker/familyTracker
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Deploy
Push to Github. Login to server and Pull. Restart service.
```
sudo systemctl status aguileraTracker.service
```
