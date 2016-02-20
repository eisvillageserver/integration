import boto3
import boto
import sys,os
from boto.s3.connection import S3Connection
import urllib

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''

bucket_name= 'eisvillageserver'
conn=boto.s3.connect_to_region("us-west-2",
       aws_access_key_id=AWS_ACCESS_KEY_ID,
       aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
       is_secure=True,
       calling_format = boto.s3.connection.OrdinaryCallingFormat(),
       )
bucket = conn.get_bucket(bucket_name,validate=False)

#make sure testing exists in folder
boto.s3.key.Key(bucket=bucket, name='0/Image/V1uofC1ix-dakjlkdf').get_contents_to_filename("testing\\test.csv")

for l in bucket:
    print(l.key)
    #Select only keys we want
    if ('0/Image/V1uofC1ix-dakjlkdf' == str(l.name)):
        url=str(l.generate_url(expires_in=60, query_auth=False, force_http=True))
        testfile = urllib.URLopener()
        testfile.retrieve(url, "test.png")
