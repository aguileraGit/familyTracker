
- [x] Push secret key and host (DB Only) to shell variables
- [x] Be sure to remove from app & add to gitignore
- [x] Create new Github repo
- [x] Pull in to RPi
- [x] Create custom config file
- [x] Create link/bookmark on phone

- [ ] Add Read me
- [ ] Add more dates (when games were created)
- [ ] Move 'Add new board game' to Settings page
- [ ] Add new family member to Settings page
- [ ] Analytics!


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