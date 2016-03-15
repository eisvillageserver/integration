# database

This database repository contains the functionality to SYNC our LOCAL server with the CLOUD server in terms of file metadata and the actual files

## Installation
This package requires the following packages to be installed as follows
* `pip install sqlalchemy`
* `pip install boto3`
* `pip install pymysql`
* `pip install boto`


## Running Sync

### Obtaining config.json
The config.json for this repository can be found in the Google Drive/Config Files/config.json

### Editing sync.py
Sync.py contains the following relevant functions:
* copyContentData(boxID, localdb, clouddb)
* syncBoxes(boxID, localdb, clouddb)

copyContentData is run the first time (and only the first time) you sync the boxes to grab all the data. The database information is written to a sqlite database called eisvsfiles.db while the physical files are downloaded into a folder labeled by the box ID.

syncBoxes runs the entire stack as follows
1. Delete Missing Files
2. Push Download Count
3. Pull Content Data

### Running sync.py
1. Open run.py
2. Edit the box id to the box desired
3. If running for the first time, create a blank file named eisvsfiles.db and then run  `python run.py`
4. If not running for the first time, comment out createBlankLocalTable and copyContentData and uncomment syncBoxes! Then run
`python sync.py`
