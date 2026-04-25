from django.core.management.base import BaseCommand
from accounts.models import Inclusion


class Command(BaseCommand):
    help = 'Seed initial inclusions'

    def handle(self, *args, **options):
        # Seed initial inclusions
        inclusions = [
            'Water',
            'Electricity',
            'Internet',
            'Cable TV',
            'Cleaning Service',
            'Laundry Service',
            'Kitchen Access',
            'Parking',
        ]

        for inclusion_name in inclusions:
            Inclusion.objects.get_or_create(name=inclusion_name)
            self.stdout.write(f'Created inclusion: {inclusion_name}')

        self.stdout.write(self.style.SUCCESS('Successfully seeded inclusions!'))
