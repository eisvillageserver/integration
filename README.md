# database

This database repository contains the functionality to SYNC our LOCAL server with the CLOUD server in terms of file metadata and the actual files

## Installation
This package requires the following packages to be installed as follows
* `pip install sqlalchemy`

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
1. Open up sync.py and scroll to the bottom of the file. 
2. Change boxID to the boxID you want to deal with
3. In CMD, run :
`python sync.py`
