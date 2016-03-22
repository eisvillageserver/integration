import sync as sync
import json
import argparse

with open('config.json') as c:
    config = json.load(c)

cloud = sync.getCloudDatabase(config["aws"]["user"], config["aws"]["password"], config["aws"]["host"], config["aws"]["port"])
local = sync.getLocalDatabase(config["sqliteDB"])
box   = config["boxID"]

def startServer():
    #app.run()
    return

def syncData():
    sync.syncBoxes(box, local, cloud);
    return

def syncFirstTime():
    sync.copyContentData(box, local, cloud);
    return


parser = argparse.ArgumentParser()
parser.add_argument('--sync', action="store_true", help="Sync server with cloud database")
parser.add_argument('--new', action="store_true", help="Create new database and sync with cloud database")
parser.add_argument('--run', action="store_true", help="Start the Village Server Web Application")

arg = parser.parse_args()

if arg.sync:
    syncData();
elif arg.new:
    syncFirstTime();
else:
    startServer();
