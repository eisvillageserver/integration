# SETUP
# pip install flask-cors
# pip install flask
# pip install sqlalchemy

# Need to install Sqlite from their website
# Anything else please add!

from flask import Flask, request, render_template
from flask_restful import Resource, Api
from sqlalchemy import create_engine
import json
from json import dumps
import api as app

with open('config.json') as c:
    config = json.load(c)

e = create_engine('sqlite:///' + config["sqliteDB"]) #connect to DB
app = Flask(__name__,static_url_path='') # Initializing our app
api = Api(app) #initializing the API


# Implementations of endpoints
## TODO: merge all the category endpoints

# Gets the latest 10 files form the database
class Latest(Resource):
    def get(self):
        conn = e.connect()
        query = conn.execute('''SELECT * FROM files ORDER BY LastUpdated DESC LIMIT 0, 9''')
        result = {'files': [dict(zip(tuple (query.keys()), i)) for i in query.cursor]}
        return result;

# Gets a list of categories from the database
class Categories(Resource):
    def get(self):
        conn = e.connect()
        query = conn.execute('''SELECT DISTINCT Category FROM files''')
        result = {'categories': [i[0] for i in query.cursor]}
        return result

# Gets a list of files with category Application from database
class Applications(Resource):
    def get(self):
        conn = e.connect()
        query = conn.execute('''SELECT * FROM files where Category == "Application" ORDER BY LastUpdated DESC''')
        result = {'files': [dict(zip(tuple (query.keys()), i)) for i in query.cursor]}
        return result;

# Gets a list of files with category Document from database
class Documents(Resource):
    def get(self):
        conn = e.connect()
        query = conn.execute('''SELECT * FROM files where Category == "Document" ORDER BY LastUpdated DESC''')
        result = {'files': [dict(zip(tuple (query.keys()), i)) for i in query.cursor]}
        return result

# Gets a list of files with category Image from database
class Images(Resource):
    def get(self):
        conn = e.connect()
        query = conn.execute('''SELECT * FROM files where Category == "Image" ORDER BY LastUpdated DESC''')
        result = {'files': [dict(zip(tuple (query.keys()), i)) for i in query.cursor]}
        return result

# Gets a list of files with category Videos from database
class Videos(Resource):
    def get(self):
        conn = e.connect()
        query = conn.execute('''SELECT * FROM files where Category == "Video" ORDER BY LastUpdated DESC''')
        result = {'files': [dict(zip(tuple (query.keys()), i)) for i in query.cursor]}
        return result;

# Gets a list of files with category Music from database
class Music(Resource):
    def get(self):
        conn = e.connect()
        query = conn.execute('''SELECT * FROM files where Category == "Music" ORDER BY LastUpdated DESC''')
        result = {'files': [dict(zip(tuple (query.keys()), i)) for i in query.cursor]}
        return result

# Sends a post request to increase the download count of a specified UID by 1
class Count(Resource):
    def post(self, uid):
        conn = e.connect()
        print "connnected"
        sql = "UPDATE files SET 'DownloadCount' = DownloadCount+1,'DownloadCountSynced'=0 WHERE UID='" + uid + "'"
        print sql
        query = conn.execute(sql)
        print query
        return "Downloaded!"

# List of all our endpoints
api.add_resource(Count, '/count/<string:uid>')
api.add_resource(Categories, '/categories/')
api.add_resource(Documents, '/categories/documents')
api.add_resource(Images, '/categories/images')
api.add_resource(Videos, '/categories/videos')
api.add_resource(Music, '/categories/music')
api.add_resource(Applications, '/categories/applications')
api.add_resource(Latest, '/latest/')

@app.route("/")
def main():
    return render_template('index.html')

# Run the API
def run():
    app.run(host='0.0.0.0', port=80, threaded=True, debug=False)
