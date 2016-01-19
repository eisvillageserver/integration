# SETUP
# pip install flask-cors
# pip install flask
# pip install sqlalchemy

# Need to install Sqlite from their website
# Anything else please add!

from flask import Flask, request
from flask_restful import Resource, Api
from flask.ext.cors import CORS
from sqlalchemy import create_engine
from json import dumps

e = create_engine('sqlite:///eisvsfiles.db') #connect to DB
app = Flask(__name__) # Create "app" (We are only using flask for API)
CORS(app) # This allows us to call our API from "somewhere else"
api = Api(app)


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
        result = {'categories': [i for i in query.cursor] }
        return result


# List of all our endpoints
api.add_resource(Files, '/files/<string:file_cat>', endpoint='files')
api.add_resource(Categories, '/categories/')

# Run the API
if __name__ == '__main__':
    app.run()
