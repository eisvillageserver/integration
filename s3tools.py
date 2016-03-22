import boto3
import boto
import sys,os
import json
from boto.s3.connection import S3Connection
import urllib
import re

with open('config.json') as c:
    config = json.load(c)

#CONNECT TO S3
conn = boto.s3.connect_to_region("us-west-2",
        aws_access_key_id = config["accessKeyId"],
        aws_secret_access_key = config["secretAccessKey"],
        is_secure = True,
        calling_format = boto.s3.connection.OrdinaryCallingFormat(),
       )

bucket_name = 'eisvillageserver'
bucket = conn.get_bucket( bucket_name, validate = False )

# Input string format: boxID/Folder/UUID-file.ext
# Output: UUID, None if UUID doesn't exists
def getKeyUUID ( key ):
    keyInfo = re.split(r'[/,-]', key.key)
    if ( len(keyInfo) > 2 ):
        return keyInfo[2]
    else:
        return None

# Input: string UUID
# Returns True if success, else False
def downloadKey ( UUID ):
    for item in bucket:
        if ( getKeyUUID(item) == UUID ): # download file if there exists an UUID
            folder = os.path.dirname("static/"+item.key)
            if not os.path.exists(folder): #make new directory only if it doesnt exist
                os.makedirs(folder)
            boto.s3.key.Key( bucket = bucket, name = item.key ).get_contents_to_filename("static/" + str(item.key)) #download it
            return True
    return False
