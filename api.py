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

e = create_engine('sqlite:///eisvsfiles.db') #connect to DB
app = Flask(__name__,static_url_path='') # Create "app" (We are only using flask for API)
api = Api(app)
CORS(app)


# Implementations of endpoints
class Files(Resource):
    def get(self, file_cat):
        conn = e.connect()
        sql = "SELECT * FROM files WHERE Category = " + '''"''' + file_cat + '''"'''
        query = conn.execute(sql)

        result = {'files': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return result

class Categories(Resource):
    def get(self):
        conn = e.connect()
        query = conn.execute('''SELECT DISTINCT Category FROM files''')
        result = {'categories': [i[0] for i in query.cursor]}
        print result
        return result

class Documents(Resource):
    def get(self):
        conn = e.connect()
        query = conn.execute('''SELECT * FROM files where Category == "Document"''')
        result = {'files': [dict(zip(tuple (query.keys()), i)) for i in query.cursor]}
        return result;

class Images(Resource):
    def get(self):
        conn = e.connect()
        query = conn.execute('''SELECT * FROM files where Category == "Image"''')
        result = {'files': [dict(zip(tuple (query.keys()), i)) for i in query.cursor]}
        return result;

class Videos(Resource):
    def get(self):
        conn = e.connect()
        query = conn.execute('''SELECT * FROM files where Category == "Video"''')
        result = {'files': [dict(zip(tuple (query.keys()), i)) for i in query.cursor]}
        return result;

class Music(Resource):
    def get(self):
        conn = e.connect()
        query = conn.execute('''SELECT * FROM files where Category == "Music"''')
        result = {'files': [dict(zip(tuple (query.keys()), i)) for i in query.cursor]}
        return result

class FilesByID(Resource):
    def get(self, numid):
        conn = e.connect()
        sql = "SELECT * FROM files WHERE UID = \'" + numid + "'"
        print sql
        query = conn.execute(sql)
        result = {'files': [dict(zip(tuple (query.keys()), i)) for i in query.cursor]}
        return result

# List of all our endpoints
#api.add_resource(Files, '/files/<string:file_cat>', endpoint='files')
api.add_resource(FilesByID, '/files/<string:numid>', endpoint='FilesById')
api.add_resource(Categories, '/categories/')
api.add_resource(Documents, '/categories/documents')
api.add_resource(Images, '/categories/images')
api.add_resource(Videos, '/categories/videos')
api.add_resource(Music, '/categories/music')

@app.route("/")
def main():
    return render_template('index.html')

# Run the API
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,threaded=True)
