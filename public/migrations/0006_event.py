import core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0005_teammember'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
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
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(max_length=1000)),
                (
                    'category',
                    models.CharField(
                        choices=[
                            ('academic', 'Academic'),
                            ('sports', 'Sports'),
                            ('culture', 'Culture & Arts'),
                            ('community', 'Community'),
                        ],
                        default='community',
                        max_length=20,
                    ),
                ),
                (
                    'image',
                    models.ImageField(
                        blank=True,
                        help_text='Recommended size: 800×500 px (maximum 5 MB)',
                        null=True,
                        upload_to='events/',
                        validators=[core.validators.validate_image_size],
                    ),
                ),
                ('start_at', models.DateTimeField()),
                (
                    'end_at',
                    models.DateTimeField(
                        blank=True,
                        help_text='When set, the event moves to Past Highlights after this time',
                        null=True,
                    ),
                ),
                ('location', models.CharField(blank=True, max_length=200)),
                (
                    'order',
                    models.PositiveIntegerField(
                        default=0,
                        help_text='Lower numbers appear first within upcoming or past events',
                    ),
                ),
                (
                    'visible',
                    models.BooleanField(
                        default=True,
                        help_text='Uncheck to hide this event from the Events page',
                    ),
                ),
            ],
            options={
                'ordering': ['order', 'start_at'],
            },
        ),
    ]
