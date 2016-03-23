import os, sys
from sqlalchemy import *
import time
import datetime
import json
import urllib2
import sqlalchemy as sa

import s3tools as s3t

f = '%Y-%m-%d %H:%M:%S'

tableData = MetaData()

files = Table('files', tableData,
    Column('UID', VARCHAR(255), primary_key=True),
    Column('Title', VARCHAR(255)),
    Column('Description', TEXT),
    Column('DateUploaded', DATETIME),
    Column('S3URI', VARCHAR(255)),
    Column('Category', VARCHAR(255)),
    Column('Language', VARCHAR(255)),
    Column('Country', VARCHAR(255)),
    Column('DownloadCount', Integer),
    Column('LastUpdated', DATETIME),
    Column('DownloadCountSynced', BOOLEAN),
    Column('BoxID', Integer)
)

# Loading data from config file
with open('config.json') as c:
    config = json.load(c)

# Get Local Database Engine
# Creates a new database with correct schema if file does not exist
def getLocalDatabase(sqliteFile):
    if os.path.isfile(sqliteFile):
        local = create_engine('sqlite:///' + sqliteFile)
        local.echo = False
        return local
    else:
        print "Database file does not exist! Creating..."
        f = open(sqliteFile, "w+")
        f.write("")
        local = create_engine('sqlite:///' + sqliteFile)
        local.echo = False
        tableData.create_all(local);
        return local

# Get Cloud Database Engine
def getCloudDatabase(user, pw, server, port):
    cloud = create_engine('mysql+pymysql://' + user + ':' + pw + '@' + server + ':' + port)
    cloud.echo = False
    return cloud

# Get the date where the box was last updated
def getLastUpdatedDate(boxID, clouddb):
    db = clouddb.connect()
    sql = "SELECT LastUpdated from eisvillageserver.boxes WHERE boxID =" + str(boxID)
    result = db.execute(sql)
    for row in result:
        return row[0];

# Get the date where the box was last synced
def getLastSyncedDate(boxID, clouddb):
    db = clouddb.connect()
    sql = "SELECT LastSynced from eisvillageserver.boxes WHERE boxID =" + str(boxID)
    result = db.execute(sql)
    for row in result:
        return row[0];

# Set the last synced date of the box to now
def updateLastSynced(boxID, clouddb):
    cloud = clouddb.connect()
    sql = "UPDATE eisvillageserver.boxes  SET LastSynced = '" + datetime.datetime.now().strftime(f) + "' WHERE (BoxID = " + str(boxID) + ")";
    print sql
    cloud.execute(sql)

    return

# For first time setup, copy entire aws file information to local db and download all files
def copyContentData(boxID, localdb, clouddb):
    cloud = clouddb.connect()
    local = localdb.connect()

    # GET DATA
    sql = "SELECT * from eisvillageserver.files WHERE boxID =" + str(boxID)
    rows = cloud.execute(sql)
    for row in rows:
        local.execute(files.insert().values(**row))

    resetDownloadCountSynced(localdb);

    sql = "SELECT UID from files"
    rows = local.execute(sql);

    for row in rows:
        s3t.downloadKey(row[0]);

    updateLastSynced(boxID, clouddb)

    return

# Set the entire column for DownloadCountSynced to False
def resetDownloadCountSynced(localdb):
    local = localdb.connect()
    sql = "UPDATE files SET 'DownloadCountSynced' = 0"
    local.execute(sql)

# Update download count to cloud
def pushDownloadCount(localdb, clouddb):
    local = localdb.connect()
    cloud = clouddb.connect()

    sql = "SELECT UID, DownloadCount from files WHERE DownloadCountSynced = 0"
    rows = local.execute(sql)
    for row in rows:
        uid = row[0]
        dlc = row[1]

        update = "UPDATE eisvillageserver.files SET DownloadCount = " + str(dlc) + " WHERE (UID ='" + uid + "')";
        print update
        cloud.execute(update);

        reset = "UPDATE files SET DownloadCountSynced = 1 WHERE (UID = '" + uid + "')"
        local.execute(reset);

    return

# Pull new file information AND update file
def pullContentData(boxID, localdb, clouddb):
    lastSynced = getLastSyncedDate(boxID, clouddb)
    cloud = clouddb.connect()
    local = localdb.connect()

    sql = "SELECT * from eisvillageserver.files WHERE LastUpdated >= '" + lastSynced.strftime(f) + "' AND BoxID = " + str(boxID)

    result = cloud.execute(sql);

    for row in result:
        old = "SELECT 'S3URI' from files WHERE UID = '{0}'".format(row[0])
        olddata = local.execute(old)


        insert = "INSERT OR REPLACE INTO files ('UID', 'Title', 'Description', 'DateUploaded', 'S3URI', 'Category', 'Language', 'Country', 'DownloadCount', 'LastUpdated', 'DownloadCountSynced', 'BoxID')"
        insert += "VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}')".format(row[0], row[1], row[2], row[3].strftime(f), row[4], row[5], row[6], row[7], row[8], row[9].strftime(f), 0, boxID)

        update = "update files set 'Title' = '{0}', 'Description' = '{1}', 'S3URI' = '{2}', 'Category' = '{3}' WHERE (UID = '{4}')".format(row[1], row[2], row[4], row[5], row[0])

        print insert
        #print update

        inserted = local.execute(insert);
        updated = local.execute(update);

        if (olddata != row[4] or not olddata): #if s3uri's don't match
            print row[0]
            s3t.downloadKey(row[0]);

        #updated = local.execute(update);


        #local.execute(sql)
    updateLastSynced(boxID, clouddb)

    return


    # if last updated date online file is more recent than local file, pull info, download file
    # set last updated to now for online and localdb

# Delete files and database info if not present
def deleteMissingFiles(boxID, localdb, clouddb):
    local = localdb.connect()
    cloud = clouddb.connect()

    liveuid = "SELECT UID from eisvillageserver.files WHERE BoxID = " + str(boxID);

    uidc = cloud.execute(liveuid)

    localuid = "SELECT UID from files"

    uidl = local.execute(localuid)

    cloudids = []
    localids = []

    for uid in uidc:
        cloudids.append(uid[0])
    for uid in uidl:
        localids.append(uid[0])

    diff = list(set(localids) - set(cloudids))
    print diff

    for uid in diff:
        sql = "SELECT S3URI from files where UID ='" + uid + "'";
        path = local.execute(sql);
        for p in path:
            uri = p[0]
            uri = "static/" + uri
            try:
                print "Removed File: " + uri
                os.remove(uri)
            except Exception:
                print "File Does not Exist: Pass"
                pass
            sql = "DELETE from files WHERE UID = '" + uid + "'"
            #local.execute(sql);
            print "Deleted " + uid

        # if delete == True:
        #     print "Deleting " + localid
        #     sql = "SELECT S3URI from files WHERE UID = '" + localid + "'";
        #     deletee = local.execute(sql);
        #     for row in deletee:
        #         uri = row[0]
        #         #uri.replace('/', '\\')
        #         uri = uri.split("/")
        #         d = "DELETE from files WHERE UID = '" + localid + "'";
        #         print d
        #         hello = local.execute(d)
        #         print "Deleted " + localid
        #         try:
        #             os.remove(uri)
        #         except:
        #             pass
        #         delete = False;

    return

# FULL SYNC FUNCTION!
def syncBoxes(boxID, localdb, clouddb):
    deleteMissingFiles(boxID, localdb, clouddb)
    pushDownloadCount(localdb, clouddb)
    pullContentData(boxID, localdb, clouddb)
    return


cloud = getCloudDatabase(config["aws"]["user"], config["aws"]["password"], config["aws"]["host"], config["aws"]["port"])
local = getLocalDatabase("eisvsfiles.db")

#pullContentData(8, local, cloud)
#syncBoxes(8, local, cloud)

#deleteMissingFiles(8, local, cloud)

#copyContentData(8, local, cloud)
