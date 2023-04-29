

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
- [ ] Be able to update User profile (add ID, Brother/Sister/Mom/Dad)
- [x] Cast points column as int
- [x] Better understand Bootstrap (See GPT history)
- [ ] Add users to make public (requires server)
- [ ] Add Random Point

https://pythonbasics.org/flask-login/
https://stackoverflow.com/questions/45701726/pandas-dataframe-to-bootstrap-table
https://plotly.com/python/templates/
https://blog.heptanalytics.com/flask-plotly-dashboard/

# Analytics
### Horizontal relative bars (Diverging horizontal stacked bar)
 - Boys vs Girls ---|-----
 - Kids vs Adult --|----- 
 - Brothers vs Sister ----|----
 - Mom vs Dad ----|-----

### Weekly Summary
Generic Fn that filters data by date and returns a DF. Each item below can pull from combinedDataDF or specificDF. 
 - Table by Fly/Board Games/Chia Seeds
 - Total points by winner
 - Games played
 - Flys killed
Note: CombinedDataDF should probably include other columns. I'm thinking boardGameDF should include game played.

# User Profile work
Shall pull all fields (including new fields) from the DB and display them in the form. Where the default values are the 
values from the DB. User can overwrite the values from the website. Disable certain values (DB ID). Add button with
some jQuery/AJAX to associate DB ID with form or create a new page that pulls data from DB per button click.

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
