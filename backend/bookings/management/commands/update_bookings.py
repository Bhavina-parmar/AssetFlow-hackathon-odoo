from django.core.management.base import BaseCommand
from bookings.utils import update_booking_statuses

class Command(BaseCommand):
    help = "Flips booking statuses (Upcoming -> Ongoing -> Completed) based on the current time."

    def handle(self, *args, **options):
        self.stdout.write("Updating booking statuses...")
        update_booking_statuses()
        self.stdout.write(self.style.SUCCESS("Successfully updated booking statuses."))
