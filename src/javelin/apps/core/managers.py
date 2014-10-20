from django.db import models


class ActiveAlertManager(models.Manager):
    def get_queryset(self):
        return super(ActiveAlertManager, self)\
            .get_queryset().exclude(status__in=('D', 'C', 'U',))


class InactiveAlertManager(models.Manager):
    def get_queryset(self):
        return super(InactiveAlertManager, self)\
            .get_queryset().filter(status__in=('D', 'C',))


class WaitingForActionAlertManager(models.Manager):
    def get_queryset(self):
        return super(WaitingForActionAlertManager, self)\
            .get_queryset().filter(status__in=('N', 'P'))


class ShouldReceiveAutoResponseAlertManager(models.Manager):
    def get_queryset(self):
        return super(ShouldReceiveAutoResponseAlertManager, self)\
            .get_queryset()\
            .filter(status__in=('N', 'P'),
                    user_notified_of_dispatcher_congestion=False,
                    initiated_by='C',
                    disarmed_time__isnull=True)


class AcceptedAlertManager(models.Manager):
    def get_queryset(self):
        return super(AcceptedAlertManager, self)\
            .get_queryset().filter(status='A')


class CompletedAlertManager(models.Manager):
    def get_queryset(self):
        return super(CompletedAlertManager, self)\
            .get_queryset().filter(status='C')


class DisarmedAlertManager(models.Manager):
    def get_queryset(self):
        return super(DisarmedAlertManager, self)\
            .get_queryset().filter(status='D')


class NewAlertManager(models.Manager):
    def get_queryset(self):
        return super(NewAlertManager, self)\
            .get_queryset().filter(status='N')


class PendingAlertManager(models.Manager):
    def get_queryset(self):
        return super(PendingAlertManager, self)\
            .get_queryset().filter(status='P')


class InitiatedByChatAlertManager(models.Manager):
    def get_queryset(self):
        return super(InitiatedByChatAlertManager, self)\
            .get_queryset().filter(initiated_by='C')


class InitiatedByEmergencyAlertManager(models.Manager):
    def get_queryset(self):
        return super(InitiatedByEmergencyAlertManager, self)\
            .get_queryset().filter(initiated_by='E')


class InitiatedByTimerAlertManager(models.Manager):
    def get_queryset(self):
        return super(InitiatedByTimerAlertManager, self)\
            .get_queryset().filter(initiated_by='T')


class InitiatedByYankAlertManager(models.Manager):
    def get_queryset(self):
        return super(InitiatedByYankAlertManager, self)\
            .get_queryset().filter(initiated_by='Y')


class InitiatedBy911AlertManager(models.Manager):
    def get_queryset(self):
        return super(InitiatedBy911AlertManager, self)\
            .get_queryset().filter(initiated_by='N')


class InitiatedByStaticDeviceAlertManager(models.Manager):
    def get_queryset(self):
        return super(InitiatedBy911AlertManager, self)\
            .get_queryset().filter(initiated_by='S')


class TrackingEntourageSessionManager(models.Manager):
    def get_queryset(self):
        return super(TrackingEntourageSessionManager, self)\
            .get_queryset().exclude(status__in=('T',))