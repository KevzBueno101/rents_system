import json
from django.core.management.base import BaseCommand
from django.core import serializers

class Command(BaseCommand):
    help = 'Dump data with UTF-8 encoding'

    def handle(self, *args, **options):
        excluded = [
            'contenttypes',
            'auth.permission',
        ]
        
        from django.apps import apps
        all_models = []
        for app_config in apps.get_app_configs():
            for model in app_config.get_models():
                label = f"{app_config.label}.{model.__name__}".lower()
                app_label = app_config.label
                if app_label not in excluded and label not in excluded:
                    all_models.append(f"{app_config.label}.{model.__name__}")

        data = serializers.serialize('json', 
            __import__('itertools').chain(*[
                apps.get_model(m).objects.all() for m in all_models
            ]),
            use_natural_foreign_keys=True,
            use_natural_primary_keys=True,
        )
        
        with open('data.json', 'w', encoding='utf-8') as f:
            f.write(data)
            
        self.stdout.write(self.style.SUCCESS('Successfully dumped data to data.json'))