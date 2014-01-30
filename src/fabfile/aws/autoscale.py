from boto.ec2 import autoscale
from boto.ec2.autoscale import (AutoScaleConnection, AutoScalingGroup,
                                LaunchConfiguration, ScalingPolicy)

from ..conf import settings
from service import BaseService


class AutoScaleService(BaseService):

    def __init__(self, settings):
        super(AutoScaleService, self).__init__(settings)
        aws_access_key_id = settings.get('EC2', 'aws_access_key_id', None)
        aws_secret_access_key =\
            settings.get('EC2', 'aws_secret_access_key', None)
        region_name = settings.get('AS', 'REGION_NAME', 'us-east-1')
        self.conn =\
            AutoScaleConnection(aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key)
        assert self.conn is not None

    def regions(self, *args, **kwargs):
        return autoscale.regions(*args, **kwargs)

    def list(self, names=[], *args, **kwargs):
        return self.conn.get_all_groups(names)

    def get_group(self, group_name):
        return self.list([group_name])

    def create_launch_configuration(self, lc_name, image_id):
        instance_type = settings.get('EC2', 'DEFAULT_INSTANCE_TYPE', None)
        launch_config = LaunchConfiguration(name=lc_name,
                                            image_id=image_id,
                                            key_name='Default',
                                            security_groups=['sg-47abe72c',],
                                            instance_type=instance_type)
        self.conn.create_launch_configuration(launch_config)
