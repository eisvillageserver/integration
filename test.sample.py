import boto3
import boto
import sys,os
from boto.s3.connection import S3Connection
import urllib

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''

#CONNECT TO S3
conn=boto.s3.connect_to_region("us-west-2",
       aws_access_key_id=AWS_ACCESS_KEY_ID,
       aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
       is_secure=True,
       calling_format = boto.s3.connection.OrdinaryCallingFormat(),
       )
bucket_name= 'eisvillageserver'
bucket = conn.get_bucket(bucket_name,validate=False)

#Input string format: boxID/Folder/UUID-file.ext
#Output: UUID, None if UUID doesn't exists
def getKeyUUID(key):
    keyInfo=re.split(r'[/,-]',key.key)
    if ( len(keyInfo) > 2):
        return keyInfo[2]
    else:
        return None
#Input: string UUID, bucket object from S3
#Returns True if success, else False
def download_S3(UUID,bucket):
    for item in bucket:
        if ( getKeyUUID(item) == UUID ): # download file if there exists an UUID
            folder=os.path.dirname(item.key)
            if not os.path.exists(folder): #make new directory only if it doesnt exist
                os.makedirs(folder)
            boto.s3.key.Key(bucket=bucket, name=item.key).get_contents_to_filename(str(item.key)) #download it
            updated= True #update db from kenya's side
            return True
    return False

print("Should return true:")
print(download_S3('V1uofC1ix',bucket)) #Should be True
print("Should return false")
print(download_S3('random',bucket)) #Should be False
