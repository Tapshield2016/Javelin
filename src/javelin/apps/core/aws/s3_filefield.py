__author__ = 'adamshare'

# ########################################################
# S3FileField.py
# Extended FileField and ImageField for use with Django and Boto.
#
# Required settings:
#	USE_AMAZON_S3 - Boolean, self explanatory
#	DEFAULT_BUCKET - String, represents the default bucket name to use if one isn't provided
#	AWS_ACCESS_KEY_ID - String
#	AWS_SECRET_ACCESS_KEY - String
#
# ########################################################

from django.db import models
from django.conf import settings
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from django.core.files.storage import FileSystemStorage
from django.core.files import File
import urllib
import os
try:
    from PIL import Image
except ImportError:
    import Image
from StringIO import StringIO

from django.conf import settings
from django.core.files.base import ContentFile

try:
    from sorl.thumbnail import ImageField
except ImportError:
    from django.db.models import ImageField


# DEFAULT_SIZE = getattr(settings, 'DJANGORESIZED_DEFAULT_SIZE', [1920, 1080])
DEFAULT_COLOR = (255, 255, 255, 0)

class S3Storage(FileSystemStorage):
    def __init__(self, bucket=None, location=None, base_url=None):
        assert bucket
        if location is None:
            location = settings.MEDIA_ROOT
        if base_url is None:
            base_url = settings.MEDIA_URL
        self.location = os.path.abspath(location)
        self.bucket = bucket
        self.base_url = base_url

    def _open(self, name, mode='rb'):
        class S3File(File):
            def __init__(self, key):
                self.key = key

            def size(self):
                return self.key.size

            def read(self, *args, **kwargs):
                return self.key.read(*args, **kwargs)

            def write(self, content):
                self.key.set_contents_from_string(content)

            def close(self):
                self.key.close()

        return S3File(Key(self.bucket, name))

    def _save(self, name, content):
        key = Key(self.bucket, name)
        if hasattr(content, 'temporary_file_path'):
            key.set_contents_from_filename(content.temporary_file_path())
        elif isinstance(content, File):
            key.set_contents_from_file(content)
        else:
            key.set_contents_from_string(content)
        # key.set_contents_from_string(key.get_contents_as_string(), {"Content-Type":"image/png"}, True)
        key.set_acl('public-read')

        return name

    def delete(self, name):
        self.bucket.delete_key(name)

    def exists(self, name):
        return Key(self.bucket, name).exists()

    def listdir(self, path):
        return [key.name for key in self.bucket.list()]

    def path(self, name):
        raise NotImplementedError

    def size(self, name):
        return self.bucket.get_key(name).size

    def url(self, name):
        return Key(self.bucket, name).generate_url(100000)

    def get_available_name(self, name):
        return name


class S3EnabledFileField(models.FileField):
    def __init__(self, bucket=settings.AWS_STORAGE_BUCKET_NAME, verbose_name=None, name=None, upload_to="", storage=None, **kwargs):
        if settings.USE_AMAZON_S3:
            self.connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            self.bucket = self.connection.get_bucket(bucket, validate=False)
            if not self.bucket:
                self.bucket = self.connection.create_bucket(bucket)
            storage = S3Storage(self.bucket)
        super(S3EnabledFileField, self).__init__(verbose_name, name, upload_to, storage, **kwargs)

class ResizedImageFieldFile(ImageField.attr_class):

    def save(self, name, content, save=True):

        new_content = StringIO()
        content.file.seek(0)
        thumb = Image.open(content.file)
        thumb.thumbnail((
            self.field.max_width,
            self.field.max_height
            ), Image.ANTIALIAS)

        img = thumb

        img.save(new_content, format=thumb.format, **img.info)

        new_content = ContentFile(new_content.getvalue())

        super(ResizedImageFieldFile, self).save(name, new_content, save)

class S3EnabledImageField(models.ImageField):

    attr_class = ResizedImageFieldFile

    def __init__(self, bucket=settings.AWS_STORAGE_BUCKET_NAME, verbose_name=None, name=None, width_field=None, height_field=None, max_width=None, max_height=None, **kwargs):

        self.max_width = kwargs.pop('max_width', max_width)
        self.max_height = kwargs.pop('max_height', max_height)

        if not self.max_width:
            self.max_width = 100000
        if not self.max_height:
            self.max_height = 100000

        if settings.USE_AMAZON_S3:
            self.connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            self.bucket = self.connection.get_bucket(bucket, validate=False)
            if not self.bucket:
                self.bucket = self.connection.create_bucket(bucket)
            kwargs['storage'] = S3Storage(self.bucket)
        super(S3EnabledImageField, self).__init__(verbose_name, name, width_field, height_field, **kwargs)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        string = self.get_prep_value(value)
        if string:
            string = '%s%s' % (settings.AWS_S3_BUCKET_URL, urllib.quote_plus(string))
        return string