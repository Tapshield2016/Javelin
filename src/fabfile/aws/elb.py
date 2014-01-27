from boto.ec2.elb import ELBConnection

from ..conf import settings
from service import BaseService


class ELBService(BaseService):
    def __init__(self, settings):
        super(ELBService, self).__init__(settings)
        aws_access_key_id = settings.get('EC2', 'aws_access_key_id', None)
        aws_secret_access_key =\
            settings.get('EC2', 'aws_secret_access_key', None)
        region_name = settings.get('ELB', 'REGION_NAME', 'us-east-1')
        self.conn = ELBConnection(aws_access_key_id=aws_access_key_id,
                                  aws_secret_access_key=aws_secret_access_key)
        assert self.conn is not None

    def regions(self, *args, **kwargs):
        return elb.regions(*args, **kwargs)

    def list(self, names=[], *args, **kwargs):
        return self.conn.get_all_load_balancers(load_balancer_names=names,
                                                *args, **kwargs)

    def zones(self, balancer, zone_names, add=True):
        if add:
            return self.conn.enable_availability_zones(balancer, zone_names)
        return self.conn.disable_availability_zones(balancer, zone_names)


#######################################
## Probably best not to use these... ##
#######################################

    #def delete(self, name):
    #    return self.conn.delete_load_balancer(name)

    #def register(self, balancer, instance_ids):
    #    return self.conn.register_instances(balancer, instance_ids)

    #def deregister(self, balancer, instance_ids):
    #    return self.conn.deregister_instances(balancer, instance_ids)
