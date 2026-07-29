import core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0004_alter_blogpost_cover_image_alter_galleryphoto_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamMember',
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
                ('name', models.CharField(max_length=150)),
                (
                    'role',
                    models.CharField(
                        help_text="Position or responsibility shown beneath the member's name",
                        max_length=150,
                    ),
                ),
                (
                    'bio',
                    models.TextField(
                        blank=True,
                        help_text='A short introduction shown on the About page',
                        max_length=500,
                    ),
                ),
                (
                    'photo',
                    models.ImageField(
                        blank=True,
                        help_text='Upload a square portrait for the best result (maximum 5 MB)',
                        null=True,
                        upload_to='team/',
                        validators=[core.validators.validate_image_size],
                    ),
                ),
                (
                    'order',
                    models.PositiveIntegerField(
                        default=0,
                        help_text='Lower numbers appear first',
                    ),
                ),
                (
                    'visible',
                    models.BooleanField(
                        default=True,
                        help_text='Uncheck to hide this member from the About page',
                    ),
                ),
            ],
            options={
                'ordering': ['order', 'name'],
            },
        ),
    ]
