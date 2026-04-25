from django.core.management.base import BaseCommand
from accounts.models import Inclusion, Appliance


class Command(BaseCommand):
    help = 'Seed initial inclusions and appliances'

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

        # Seed initial appliances
        appliances = [
            'Fan',
            'Air Conditioner',
            'Refrigerator',
            'TV',
            'WiFi Router',
            'Microwave',
            'Electric Kettle',
            'Rice Cooker',
            'Washing Machine',
            'Water Heater',
        ]

        for appliance_name in appliances:
            Appliance.objects.get_or_create(name=appliance_name)
            self.stdout.write(f'Created appliance: {appliance_name}')

        self.stdout.write(self.style.SUCCESS('Successfully seeded inclusions and appliances!'))
