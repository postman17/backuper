import os
import traceback

from project import celery_app
from celery.utils.log import get_task_logger

from django.utils.translation import gettext_lazy as _

from backup.models import Backup, ServiceForBackup, BackupClient
from backup.matcher import BACKUP_CLIENT_MANAGERS_MATCHER
from backup.enums import BackupStatusEnum
from core.models import FileObject


task_logger = get_task_logger(__name__)


@celery_app.task
def backup_by_service(service_id, client_id, backup_id):
    task_logger.info(
        (
            f"Backup by service: started, "
            f"service_id={service_id}, "
            f"client_id={client_id}, "
            f"backup_id={backup_id}"
        )
    )
    backup_record = Backup.objects.filter(
        id=backup_id
    ).first()
    if not backup_record:
        text = f"Backup by service: backup record not found, id={backup_id}"
        backup_record.set_status(BackupStatusEnum.FAILED, description=text)
        task_logger.error(text)

        return _("Backup record not found")

    service_record = ServiceForBackup.objects.filter(id=service_id).first()
    if not service_record:
        text = f"Backup by service: service record not found, id={service_id}"
        backup_record.set_status(BackupStatusEnum.FAILED, description=text)
        task_logger.error(text)

        return _("Service record not found")

    client_record = BackupClient.objects.filter(id=client_id).first()
    if not client_record:
        text = f"Backup by service: client record not found. id={client_id}"
        backup_record.set_status(BackupStatusEnum.FAILED, description=text)
        task_logger.error(text)

        return _("Client record not found")

    try:
        filename = BACKUP_CLIENT_MANAGERS_MATCHER.execute_backup(
            client_record, service_record, backup_record, logger=task_logger
        )
    except Exception as exc:
        backup_record.set_status(BackupStatusEnum.FAILED, description=traceback.format_exc())
        task_logger.error(
            (
                f"Backup by service: execute backup error, "
                f"{repr(backup_record)}, "
                f"{repr(service_record)}, "
                f"{repr(client_record)}",
            ),
            exc_info=True
        )

        return str(exc)

    file_record = FileObject(name=os.path.basename(filename))
    file_record.file.name = filename.replace("/app/media/", "")
    file_record.save()

    backup_record.files.add(file_record)
    task_logger.info(
        (
            f"Backup by service: finished, "
            f"{repr(file_record)}, "
            f"{repr(backup_record)}, "
            f"{repr(service_record)}, "
            f"{repr(client_record)}",
        )
    )

    return True


@celery_app.task
def backup(backup_id):
    task_logger.info("Backup task: started")
    backup_record = Backup.objects.filter(
        id=backup_id
    ).prefetch_related(
        "backups",
        "services",
        "clients",
    ).first()
    if not backup_record:
        task_logger.error("Backup task: backup record not found")
        return _("Backup record not found")

    backup_record.set_status(BackupStatusEnum.STARTED)

    for children_backup_record in backup_record.backups.all():
        backup.delay(children_backup_record.id)

    for service_record in backup_record.services.all():
        for client_record in backup_record.clients.all():
            backup_by_service.delay(service_record.id, client_record.id, backup_id)

    task_logger.info(f"Backup task: finished, {repr(backup_record)}")
    return _("Backup task: finished")
