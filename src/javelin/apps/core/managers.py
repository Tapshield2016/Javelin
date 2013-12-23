from django.db import models


class ActiveAlertManager(models.Manager):
    def get_queryset(self):
        return super(ActiveAlertManager, self)\
            .get_queryset().exclude(status__in=('D', 'C'))


class InactiveAlertManager(models.Manager):
    def get_queryset(self):
        return super(InactiveAlertManager, self)\
            .get_queryset().filter(status__in=('D', 'C'))


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