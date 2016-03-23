import os, sys
from sqlalchemy import *
import time
import datetime
import json
import urllib2
import sqlalchemy as sa
import s3tools as s3t

f = '%Y-%m-%d %H:%M:%S' # date format for SQL Datetime to go into our database

# Table Schema used to create database table when initializing database
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

# Get Local Database Engine used with sqlalchemy
# Creates a new database with correct schema if file does not exist
# requires: sqliteFile - string of database file name
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

# Gets the engine for the cloud database engine
# requires: username, password, server, port (retrievable from AWS)
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

# If initializing database for the first time, copy all relevant rows from the
# files database and download all content for a specific boxID
def copyContentData(boxID, localdb, clouddb):
    cloud = clouddb.connect()
    local = localdb.connect()

    # Grabs data
    sql = "SELECT * from eisvillageserver.files WHERE boxID =" + str(boxID)
    rows = cloud.execute(sql)
    for row in rows:
        local.execute(files.insert().values(**row))

    resetDownloadCountSynced(localdb);

    sql = "SELECT UID from files"  # Find all UIDs so they can be downloaded
    rows = local.execute(sql);

    for row in rows:
        s3t.downloadKey(row[0]);

    updateLastSynced(boxID, clouddb) # Set last synced to now!

    return

# Set the entire column for DownloadCountSynced to False
def resetDownloadCountSynced(localdb):
    local = localdb.connect()
    sql = "UPDATE files SET 'DownloadCountSynced' = 0"
    local.execute(sql)

# Update download count to cloud, resets local download count back to 0
# after update and sets DownloadCountSynced to true so unless the download
# count is updated, stale information isn't constantly pushed
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

# Pull content data syncs the local database with the cloud database, pulling any
# new files/renaming files to match the S3 bucket and database on AWS
def pullContentData(boxID, localdb, clouddb):
    lastSynced = getLastSyncedDate(boxID, clouddb)
    cloud = clouddb.connect()
    local = localdb.connect()

    # Grab all files from AWS that have been updated since our last sync
    sql = "SELECT * from eisvillageserver.files WHERE LastUpdated >= '" + lastSynced.strftime(f) + "' AND BoxID = " + str(boxID)

    result = cloud.execute(sql);

    # insert the file to the database if it does not exist, else update
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

        if (olddata != row[4] or not olddata): #if new url doesn't match old one
            print row[0]
            s3t.downloadKey(row[0]);    # download the new file

        #updated = local.execute(update);


        #local.execute(sql)
    updateLastSynced(boxID, clouddb)

    return


# Checks local database against cloud database, if a file or entry exists in
# local but doesn't in the cloud, the file gets deleted. This is run first
# to minimize the amount of files we'll actually have to download.
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
            local.execute(sql);
            print "Deleted " + uid

    return

# FULL SYNC FUNCTION!
# Missing files are deleted first to reduce the amount of queries we'll have to run
# Download count is then pushed to the cloud
# Files and metadata are then synced
def syncBoxes(boxID, localdb, clouddb):
    deleteMissingFiles(boxID, localdb, clouddb)
    pushDownloadCount(localdb, clouddb)
    pullContentData(boxID, localdb, clouddb)
    return


## BELOW ARE EXAMPLES OF USING THE DATABASE FUNCTIONS
# cloud = getCloudDatabase(config["aws"]["user"], config["aws"]["password"], config["aws"]["host"], config["aws"]["port"])
# local = getLocalDatabase("eisvsfiles.db")
