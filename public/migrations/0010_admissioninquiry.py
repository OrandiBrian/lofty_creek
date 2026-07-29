import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0009_normalize_event_dates'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdmissionInquiry',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('parent_name', models.CharField(max_length=200)),
                ('phone_number', models.CharField(max_length=20)),
                (
                    'grade_level',
                    models.CharField(
                        choices=[
                            ('ecde', 'Kindergarten (ECDE)'),
                            ('lower-primary', 'Lower Primary (G1-3)'),
                            ('upper-primary', 'Upper Primary (G4-6)'),
                        ],
                        max_length=30,
                    ),
                ),
                ('received_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_read', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Admission inquiries',
                'ordering': ['-received_at'],
            },
        ),
    ]
