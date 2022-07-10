from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Create superuser"

    def add_arguments(self, parser):
        parser.add_argument("-u", "--username", default="admin", help="Username")
        parser.add_argument("-e", "--email", default="admin@admin.ru", help="Email")
        parser.add_argument("-p", "--password", default="admin", help="Password")

    def handle(self, *args, **options):
        User.objects.create_superuser(
            username=options["username"],
            email=options["email"],
            password=options["password"],
        )
        self.stdout.write(self.style.SUCCESS("Superuser created"))
