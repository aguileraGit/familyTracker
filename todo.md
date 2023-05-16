# More to do

- [ ] Move 'Add new board game' to Settings page
- [ ] Add new family member to Settings page

- [ ] Update profile to be nicer (add photos)

- [ ] Add users to make public (requires server)


https://pythonbasics.org/flask-login/
https://stackoverflow.com/questions/45701726/pandas-dataframe-to-bootstrap-table
https://plotly.com/python/templates/
https://blog.heptanalytics.com/flask-plotly-dashboard/


### Weekly Summary
Generic Fn that filters data by date and returns a DF. Each item below can pull from combinedDataDF or specificDF. 
 - Table by Fly/Board Games/Chia Seeds
 - Total points by winner
 - Games played
 - Flys killed
Note: CombinedDataDF should probably include other columns. I'm thinking boardGameDF should include game played.


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
