import boto
from boto.ec2 import EC2Connection

from ..conf import settings
from service import BaseService
from elb import ELBService


class EC2Service(BaseService):
    def __init__(self, settings):
        super(EC2Service, self).__init__(settings)
        #region_name = settings.get('EC2', 'REGION_NAME', 'us-west-1')
        #self.conn = ec2.connect_to_region(region_name=region_name)
        aws_access_key_id = settings.get('EC2', 'aws_access_key_id', None)
        aws_secret_access_key =\
            settings.get('EC2', 'aws_secret_access_key', None)
        region_name = settings.get('ELB', 'REGION_NAME', 'us-east-1')
        self.conn = EC2Connection(aws_access_key_id=aws_access_key_id,
                                  aws_secret_access_key=aws_secret_access_key)
        assert self.conn is not None

    def list(self, elb=None, *args, **kwargs):
        if elb is not None:
            return self.list_in_elb(elb)
        return self.conn.get_all_instances(*args, **kwargs)

    def list_in_elb(self, name):
        instances = []
        elb = ELBService(self.settings)
        for i in elb.list(name):
            instances.extend(i.instances)

        # Return reservations
        return self.conn.get_all_instances([i.id for i in instances])

    def regions(self, *args, **kwargs):
        return ec2.regions(*args, **kwargs)

    def resolve_instances(self, reservations):
        instances = []
        for reservation in reservations:
            for i in reservation.instances:
                instances.append(i)
        return instances

    def resolve_hosts(self, reservations):
        instances = self.resolve_instances(reservations)
        hosts = [i.public_dns_name for i in instances]
        hosts.sort()
        return hosts

    def start(self, instance_ids):
        return self.conn.start_instances(instance_ids)

    def stop(self, instance_ids, force=False):
        return self.conn.stop_instances(instance_ids, force)

    def terminate(self, instance_ids):
        return self.conn.terminate_instances(instance_ids)

    def create_image(self, instance_id, name, description=None, no_reboot=False):
        return self.conn.create_image(instance_id, name, description, no_reboot)

    def images(self, image_ids=None, *args, **kwargs):
        return self.conn.get_all_images(image_ids, *args, **kwargs)
