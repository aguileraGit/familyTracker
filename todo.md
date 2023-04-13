
- [x] Push secret key and host (DB Only) to shell variables
- [x] Be sure to remove from app & add to gitignore
- [ ] Create new Github repo
- [ ] Pull in to RPi
- [ ] Create custom config file
- [ ] Create link/bookmark on phone

- [ ] Add more dates (when games were created)


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