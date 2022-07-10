from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Create user"

    def add_arguments(self, parser):
        parser.add_argument("-u", "--username", default="user", help="Username")
        parser.add_argument("-e", "--email", default="user@user.ru", help="Email")
        parser.add_argument("-p", "--password", default="user", help="Password")

    def handle(self, *args, **options):
        user = User.objects.create(
            username=options["username"],
            email=options["email"],
            is_staff=True,
        )
        user.set_password(options["password"])
        user.save()
        self.stdout.write(self.style.SUCCESS("User created"))
