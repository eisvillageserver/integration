# SETUP
# pip install flask-cors
# pip install flask
# pip install sqlalchemy

# Need to install Sqlite from their website
# Anything else please add!

from flask import Flask, request, render_template
from flask_restful import Resource, Api
from flask.ext.cors import CORS
from sqlalchemy import create_engine
from json import dumps
import api as app

e = create_engine('sqlite:///eisvsfiles.db') #connect to DB
app = Flask(__name__,static_url_path='') # Create "app" (We are only using flask for API)
api = Api(app)


# Implementations of endpoints
## TODO: merge all the category endpoints

class Latest(Resource):
    def get(self):
        conn = e.connect()
        query = conn.execute('''SELECT * FROM files ORDER BY LastUpdated DESC LIMIT 0, 9''')
        result = {'files': [dict(zip(tuple (query.keys()), i)) for i in query.cursor]}
        return result;

class Categories(Resource):
    def get(self):
        conn = e.connect()
        query = conn.execute('''SELECT DISTINCT Category FROM files''')
        result = {'categories': [i[0] for i in query.cursor]}
        return result

class Applications(Resource):
    def get(self):
        conn = e.connect()
        query = conn.execute('''SELECT * FROM files where Category == "Application" ORDER BY LastUpdated DESC''')
        result = {'files': [dict(zip(tuple (query.keys()), i)) for i in query.cursor]}
        return result;

class Documents(Resource):
    def get(self):
        conn = e.connect()
        query = conn.execute('''SELECT * FROM files where Category == "Document" ORDER BY LastUpdated DESC''')
        result = {'files': [dict(zip(tuple (query.keys()), i)) for i in query.cursor]}
        return result

class Images(Resource):
    def get(self):
        conn = e.connect()
        query = conn.execute('''SELECT * FROM files where Category == "Image" ORDER BY LastUpdated DESC''')
        result = {'files': [dict(zip(tuple (query.keys()), i)) for i in query.cursor]}
        return result

class Videos(Resource):
    def get(self):
        conn = e.connect()
        query = conn.execute('''SELECT * FROM files where Category == "Video" ORDER BY LastUpdated DESC''')
        result = {'files': [dict(zip(tuple (query.keys()), i)) for i in query.cursor]}
        return result;

class Music(Resource):
    def get(self):
        conn = e.connect()
        query = conn.execute('''SELECT * FROM files where Category == "Music" ORDER BY LastUpdated DESC''')
        result = {'files': [dict(zip(tuple (query.keys()), i)) for i in query.cursor]}
        return result

class Apps(Resource):
    def get(self):
        conn = e.connect()
        query = conn.execute('''SELECT * FROM files where Category == "Application" ORDER BY LastUpdated DESC''')
        result = {'files': [dict(zip(tuple (query.keys()), i)) for i in query.cursor]}
        return result

class Count(Resource):
    def post(self, uid):
        conn = e.connect()
        print "connnected"
        sql = "UPDATE files SET 'DownloadCount' = DownloadCount+1,'DownloadCountSynced'=0 WHERE 'UID'='" + uid + "'"
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
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)
