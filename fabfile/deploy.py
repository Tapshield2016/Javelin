from fabric.api import run
from fabric.context_managers import cd, prefix
from fabric.decorators import roles, task

from utils import virtualenv


@task
@virtualenv
def update_repo():
    run('git pull origin develop')


@task
@virtualenv
def collectstatic():
    run('./manage.py collectstatic --noinput')


@task
@virtualenv
def restart_app_service():
    run('sudo service javelin restart')


@task
@virtualenv
def restart_queue_service():
    run('sudo service celery restart')


@task
@virtualenv
def run_migrations():
    run('./manage.py syncdb')
    run('./manage.py migrate')


@task
@virtualenv
def install_pip_requirements():
    run('pip install -r ../requirements.txt')


@task
@virtualenv
def deploy_simple(restart=True):
    update_repo()
    if eval(restart):
        restart_app_service()


@task
@virtualenv
def deploy_static(restart=False):
    update_repo()
    collectstatic()
    if eval(restart):
        restart_app_service()
