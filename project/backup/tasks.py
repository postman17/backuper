from project import celery_app

from django.utils.translation import gettext_lazy as _

from backup.models import Backup, ServiceForBackup, BackupClient
from backup.matcher import BACKUP_CLIENT_MANAGERS_MATCHER


@celery_app.task
def backup_by_service(service_id, client_id):
    service_record = ServiceForBackup.objects.filter(id=service_id).first()
    if not service_record:
        return _("Service record not found")

    client_record = BackupClient.objects.filter(id=client_id).first()
    if not client_record:
        return _("Client record not found")

    try:
        BACKUP_CLIENT_MANAGERS_MATCHER.execute_backup(client_record, service_record)
    except Exception as exc:
        return str(exc)

    return True


@celery_app.task
def backup(backup_id):
    backup_record = Backup.objects.filter(
        id=backup_id
    ).prefetch_related(
        "backups",
        "services",
        "clients",
    ).first()
    if not backup_record:
        return _("Backup record not found")

    for children_backup_record in backup_record.backups.all():
        backup.delay(children_backup_record.id)

    for service_record in backup_record.services.all():
        for client_record in backup_record.clients.all():
            backup_by_service.delay(service_record.id, client_record.id)

    return _("Backup started")
