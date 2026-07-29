from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0007_import_existing_events'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='start_at',
            new_name='start_date',
        ),
        migrations.RenameField(
            model_name='event',
            old_name='end_at',
            new_name='end_date',
        ),
        migrations.AlterField(
            model_name='event',
            name='start_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='event',
            name='end_date',
            field=models.DateField(
                blank=True,
                help_text='When set, the event moves to Past Highlights after this date',
                null=True,
            ),
        ),
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['order', 'start_date']},
        ),
    ]
