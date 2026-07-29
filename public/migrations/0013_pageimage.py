import core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0012_alter_admissioninquiry_grade_level'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageImage',
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
                (
                    'slot',
                    models.CharField(
                        choices=[
                            ('home_hero', 'Home — Hero image'),
                            ('home_about_1', 'Home — About our school image 1'),
                            ('home_about_2', 'Home — About our school image 2'),
                            ('home_about_3', 'Home — About our school image 3'),
                            ('home_about_4', 'Home — About our school image 4'),
                            ('about_story', 'About — Our story'),
                            ('about_activity_1', 'About — Outdoors & activities: Various Classes'),
                            ('about_activity_2', 'About — Outdoors & activities: Environment'),
                            ('about_activity_3', 'About — Outdoors & activities: Gardening'),
                            ('about_activity_4', 'About — Outdoors & activities: Music'),
                            ('about_activity_5', 'About — Outdoors & activities: Foreign Languages'),
                            ('about_activity_6', 'About — Outdoors & activities: Fitness'),
                            ('academics_approach', 'Academics — Our approach'),
                            ('academics_support', 'Academics — Student support'),
                        ],
                        help_text='Choose the exact page location where this photo should appear.',
                        max_length=40,
                        unique=True,
                    ),
                ),
                (
                    'image',
                    models.ImageField(
                        help_text='Recommended size: at least 1200×800 px (maximum 5 MB).',
                        upload_to='page-images/',
                        validators=[core.validators.validate_image_size],
                    ),
                ),
                (
                    'alt_text',
                    models.CharField(
                        blank=True,
                        help_text='Optional image description for accessibility.',
                        max_length=180,
                    ),
                ),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Page image',
                'verbose_name_plural': 'Page images',
                'ordering': ['slot'],
            },
        ),
    ]
