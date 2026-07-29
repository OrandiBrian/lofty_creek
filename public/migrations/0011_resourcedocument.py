import core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0010_admissioninquiry'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResourceDocument',
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
                ('description', models.TextField(blank=True, max_length=500)),
                (
                    'document',
                    models.FileField(
                        help_text='Upload a document up to 10 MB',
                        upload_to='resources/',
                        validators=[core.validators.validate_document_size],
                    ),
                ),
                (
                    'document_type',
                    models.CharField(
                        choices=[
                            ('pdf', 'PDF document'),
                            ('form', 'Form'),
                            ('guide', 'Guide'),
                            ('other', 'Other document'),
                        ],
                        default='pdf',
                        max_length=20,
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
                        help_text='Uncheck to hide this download from the Resources page',
                    ),
                ),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['order', 'title'],
            },
        ),
    ]
