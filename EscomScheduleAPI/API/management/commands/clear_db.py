from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = (
        "Remove ALL data from the database while keeping the tables. "
        "Run with --confirm to actually perform the operation."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Actually perform the flush without prompting.",
        )

    def handle(self, *args, **options):
        if not options.get("confirm"):
            self.stdout.write(self.style.WARNING("This will remove ALL data from the database."))
            self.stdout.write(self.style.WARNING("Re-run with --confirm to proceed."))
            return

        self.stdout.write("Running flush (clearing all data)...")
        # call Django's flush management command non-interactively
        call_command("flush", interactive=False)
        self.stdout.write(self.style.SUCCESS("Database cleared (tables preserved)."))
