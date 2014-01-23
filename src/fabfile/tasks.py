from fabric.decorators import task

from aws.elb import ELBService
from aws.ec2 import EC2Service
from conf import settings


@task
def list_elbs():
    service = ELBService(settings)
    print service.list()

@task
def list_elb_instances(name):
    service = EC2Service(settings)
    reservations = service.list_in_elb(name)
    print service.resolve_instances(reservations)
    print service.resolve_hosts(reservations)
