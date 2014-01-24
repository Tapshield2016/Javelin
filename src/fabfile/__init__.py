import conf
import tasks

from fabric.api import env


env.user = 'ubuntu'
env.key_filename = '~/.ec2/tapshield-default.pem'
env.ssh_config_path = '/etc/ssh_config'
env.use_ssh_config = True
env.roledefs = {
    'dev': ['devjavelin'],
    'demo': ['demojavelin'],
    'staging': ['stagingjavelin'],
    'prod': tasks.list_production_elb_instances,
}
