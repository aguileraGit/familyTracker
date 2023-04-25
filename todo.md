
- [x] Add Family Members
- [ ] Add Readme
- [x] Add more dates (when games were created)
- [ ] Move 'Add new board game' to Settings page
- [ ] Add new family member to Settings page
- [x] Analytics - Create class to get data
- [ ] Analytics - Move getData to new class and break up (get data & plot)
- [ ] Analytics - Show more plots
- [ ] Put a badge next to each person with points
- [ ] Update form to be nicer
- [ ] Update profile to be nicer
- [x] Better understand Bootstrap (See GPT history)
- [ ] Add users to make public (requires server)

https://pythonbasics.org/flask-login/
https://stackoverflow.com/questions/45701726/pandas-dataframe-to-bootstrap-table
https://plotly.com/python/templates/
https://blog.heptanalytics.com/flask-plotly-dashboard/

# Analytics
 - Boys vs Girls ---|-----
 - Kids vs Adult --|----- 
 - Weekly Summary


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