# Generated for the room media directory refactor.

from django.db import migrations, models
import django.db.models.deletion
import accounts.models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0033_roomimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to=accounts.models.room_primary_upload_path),
        ),
        migrations.AlterField(
            model_name='roomimage',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='additional_images', to='accounts.room'),
        ),
        migrations.AlterField(
            model_name='roomimage',
            name='image',
            field=models.ImageField(upload_to=accounts.models.room_additional_upload_path),
        ),
        migrations.AlterField(
            model_name='roomimage',
            name='order',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
