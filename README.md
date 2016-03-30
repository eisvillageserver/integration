# integration
This repository is a combination of 3 previous repositories: database, webapp and api. The relevant information about running all of the individual components are below.

The three functions integration currently serve are:
* python run.py --new
* python run.py --sync
* python run.py --run


## --new
This command will create a new database file based on the name in the config file and download all the relevant content from AWS S3 into the static folder. This should only be run once when you first setup the box.

## --sync
This command syncs the boxes current data with the database on AWS. This includes deleting missing files, pushing download count and downloading new files

## --run
This command runs the server, webapp and api all in one :)


## Installation
This package requires the following packages to be installed as follows
* `pip install sqlalchemy`
* `pip install boto`
* `pip install pymysql`
* `pip install flask`
* `pip install flask_restful`

In addition, you will need to go to /static/js/app.js and change the host value to whatever IP your raspberry pi is using (https://github.com/eisvillageserver/integration/blob/master/static/js/app.js line 3)

## Running Sync

### Obtaining config.json
The config.json for this repository can be found in the Google Drive/Config Files/config.json

Sync has now been streamlined, you only have to run `python run.py --new` if syncing for the first time or `python run.py --sync` otherwise.
Sync only handles files that have been changed to minimize the amount of data that is sent through GSM (thus reducing data costs).

# api
The api repository is a REST client used by our webapp to access the information in the database.

## Setup
1. Clone `eisvillageserver/database` and run the copyContentData and syncBoxes function to obtain an up to date copy of `eisvsfiles.db`
2. Copy the generated `eisvsfiles.db` into the root of this repository
3. Run `pip install flask`
4. Run `pip install flask_restful`
5. Run `pip install sqlalchemy`
6. Run `pip install flask-cors`
7. Run `python api.py`

## API
Using your favourite rest client.:
### GET /categories
Returns a list of categories of files
### GET /categories/documents
Returns a list of files with the category Documents
### GET /categories/images
Returns a list of files with the category Images
### GET /categories/music
Returns a list of files with the category Music
### GET /categories/apps
TODO: Returns a list of files with the category Applications
### GET /categories/videos
Returns a list of files with category Videos
### POST /:id
TODO: Increase the download count of the file with UID id

# webapp
The webapp is built using AngularJS and is run on our flask webserver that hosts our api. To view the webapp run `python run.py --run`

## Compiling SASS changes
1. Install Ruby
2. Install SASS
3. In the root of the integration repository, run `compass watch`
4. The css should be compiled and can be found in /static/css
