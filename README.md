# api
The api repository is a REST client used by our webapp to access the information in the database.

NOTE: In the future, the integration file will deal with the api and generating the database files. 

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
