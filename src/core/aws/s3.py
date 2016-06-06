from urlparse import urlparse

from django.conf import settings

from boto.s3.connection import S3Connection, OrdinaryCallingFormat


class S3Manager(object):

    def __init__(self):
        self.connection = self.get_s3_connection()

    def get_s3_connection(self):
        return S3Connection(\
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            calling_format=OrdinaryCallingFormat())

    def delete_file(self, url):
        aws_hostname = 's3.amazonaws.com'
        parsed = urlparse(url)
        netloc = parsed.netloc
        path = parsed.path
        if netloc.find(".%s" % aws_hostname) > 0:
            # http://<bucket_name>.s3.amazonaws.com case...
            bucket_name = netloc.split(".%s" % aws_hostname)[0]
            path = path[1:]
        else:
            # http://s3.amazonaws.com/<bucket_name>/... case...
            bucket_name = path.split('/')[1]
            path = '/'.join(path.split('/')[2:])

        bucket = self.connection.get_bucket(bucket_name)
        return bucket.delete_key(path)
            
