from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0011_resourcedocument'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admissioninquiry',
            name='grade_level',
            field=models.CharField(
                choices=[
                    ('ecde', 'Playgroup / PP1 / PP2 (ECDE)'),
                    ('lower-primary', 'Lower Primary (G1-3)'),
                    ('upper-primary', 'Upper Primary (G4-6)'),
                ],
                max_length=30,
            ),
        ),
    ]
