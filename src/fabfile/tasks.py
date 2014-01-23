from fabric.decorators import task

from aws.elb import ELBService
from conf import settings


@task
def list_elbs():
    service = ELBService(settings)
    print service.list()
