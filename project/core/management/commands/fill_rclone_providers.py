from django.core.management.base import BaseCommand

from backup.models import RCloneProvider

from helpers.rclone import RClone


class Command(BaseCommand):
    help = "Fill RClone providers model"

    def handle(self, *args, **options):
        client = RClone()
        response = client.get_all_providers()
        if response["error"]:
            self.stdout.write(self.style.ERROR(f"RClone error - {response['error']}"))

        for provider in response["out"]:
            RCloneProvider.objects.update_or_create(
                name=provider["Name"],
                defaults={
                    "description": provider["Description"],
                    "prefix": provider["Prefix"],
                }
            )
        self.stdout.write(self.style.SUCCESS("Filling providers is succeed"))
