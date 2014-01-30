import conf
import tasks
import deploy

from fabric.api import env


env.user = 'ubuntu'
env.virtualenv = 'javelin'
env.virtualenvwrapper = 'source /usr/local/bin/virtualenvwrapper.sh'
env.key_filename = '~/.ec2/tapshield-default.pem'
env.ssh_config_path = '/etc/ssh_config'
env.use_ssh_config = True
env.roledefs = {
    'dev': ['devjavelin'],
    'demo': ['demojavelin'],
    'staging': ['stagingjavelin'],
    'prod': tasks.list_production_elb_instances,
}
