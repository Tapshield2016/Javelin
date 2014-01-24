import datetime
import time

from fabric.api import run
from fabric.context_managers import cd, prefix
from fabric.decorators import roles, task

from aws.elb import ELBService
from aws.ec2 import EC2Service
from conf import settings


@task
def list_production_elb_instances():
    elb_name = settings.get('Environment', 'PRODUCTION_LOAD_BALANCER', None)
    hostnames = list_elb_instances_by_hostname(elb_name)
    return hostnames

@task
def list_elbs():
    service = ELBService(settings)
    print service.list()

@task
def list_elb_instances_by_hostname(name):
    service = EC2Service(settings)
    reservations = service.list_in_elb(name)
    return service.resolve_hosts(reservations)

@task
def add_availability_zone_to_elb(elb_name, az_name):
    service = ELBService(settings)
    print service.zones(elb_name, [az_name], add=True)

@task
def start_staging_instance():
    service = EC2Service(settings)
    instance_id = settings.get('Environment', 'STAGING_EC2_INSTANCE_ID', None)
    instances = service.start([instance_id])
    if instances:
        instance = instances[0]
        while(True):
            instance.update()
            if instance.state == "running":
                print "Instance %s is now running." % instance_id
                return instance
            else:
                print "Still waiting on %s, status is %s" % (instance_id,
                                                             instance.state)
            time.sleep(15)
    else:
        print "No instances returned from service.start()"

@task
def stop_staging_instance():
    service = EC2Service(settings)
    instance_id = settings.get('Environment', 'STAGING_EC2_INSTANCE_ID', None)
    print service.stop([instance_id])

@task
def get_staging_instance_status():
    instance_id = settings.get('Environment', 'STAGING_EC2_INSTANCE_ID', None)
    resp = get_instance_status(instance_id)
    if resp:
        print "%s status: '%s'" % (instance_id, resp[0].instances[0].state)

@task
def get_instance_status(instance_id):
    service = EC2Service(settings)
    return service.instance_status([instance_id])

@task
def create_production_image_from_staging_instance():
    instance_id = settings.get('Environment', 'STAGING_EC2_INSTANCE_ID', None)
    service = EC2Service(settings)
    image_name = get_image_name("Production")
    print service.create_image(instance_id, image_name, no_reboot=True)

def get_image_name(environment):
    return "Javelin %s Image %s"\
        % (environment,
           datetime.datetime.now().strftime("%m/%d/%Y %I%M%p"))
