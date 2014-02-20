import csv

from optparse import make_option

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from core.models import Agency, Alert


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--agency',
            dest='agency',
            help='The numerical ID of the agency to report on'),
        )


    def handle(self, *args, **options):
        agency_id = int(options['agency'])
        agency = Agency.objects.get(pk=agency_id)
        alerts = Alert.completed\
            .select_related('agency_user', 'agency_dispatcher')\
            .prefetch_related('locations')\
            .filter(agency=agency)
        local_report_path =\
            "/home/ubuntu/%s_report.csv" % slugify(agency.name)
        columns = ["Alerter Email",
                   "Alerter Name",
                   "Dispatcher",
                   "Alert Time",
                   "Alert Type",
                   "Accepted Time",
                   "Completed Time",
                   "First Location",
                   "Last Location"]

        with open(local_report_path, 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns)
            for alert in alerts:
                first_loc = ''
                last_loc = ''
                locations = alert.locations.all()
                if locations:
                    last_loc = locations[0]
                    first_loc = locations.reverse()[0]
                writer.writerow([
                        alert.agency_user.email,
                        alert.agency_user.get_full_name(),
                        alert.agency_dispatcher,
                        alert.creation_date,
                        alert.get_initiated_by_display(),
                        alert.accepted_time,
                        alert.completed_time,
                        "%f, %f" % (first_loc.latitude, first_loc.longitude),
                        "%f, %f" % (last_loc.latitude, last_loc.longitude),
                        ])
