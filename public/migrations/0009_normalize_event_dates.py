from django.db import migrations


def normalize_sqlite_dates(apps, schema_editor):
    if schema_editor.connection.vendor != 'sqlite':
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "UPDATE public_event "
            "SET start_date = substr(start_date, 1, 10), "
            "end_date = CASE "
            "WHEN end_date IS NULL THEN NULL "
            "ELSE substr(end_date, 1, 10) END"
        )


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0008_event_dates_only'),
    ]

    operations = [
        migrations.RunPython(normalize_sqlite_dates, migrations.RunPython.noop),
    ]
