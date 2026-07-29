from datetime import datetime
from zoneinfo import ZoneInfo

from django.db import migrations, models


NAIROBI = ZoneInfo('Africa/Nairobi')


def at(year, month, day, hour=9, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=NAIROBI)


def import_existing_events(apps, schema_editor):
    Event = apps.get_model('public', 'Event')
    events = [
        {
            'title': 'End of Term Examination Week',
            'description': 'All students from Grade 1 to Grade 6 will sit for end-of-term examinations. Parents are reminded to ensure students are well rested and have all stationery materials.',
            'category': 'academic',
            'start_at': at(2026, 4, 25, 7, 30),
            'end_at': at(2026, 5, 2, 12, 30),
            'location': 'All Classrooms',
            'legacy_image_url': 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=600&h=300&fit=crop',
        },
        {
            'title': 'Inter-School Athletics Day',
            'description': 'Come cheer on our students at the annual inter-school athletics competition, including sprints, relay races, long jump, and hurdles.',
            'category': 'sports',
            'start_at': at(2026, 5, 10, 8),
            'end_at': at(2026, 5, 10, 16),
            'location': 'School Sports Ground',
            'legacy_image_url': 'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=600&h=300&fit=crop',
        },
        {
            'title': 'PTA Mid-Year Meeting',
            'description': 'Parents and guardians meet to discuss academic progress, school improvements, and term two.',
            'category': 'community',
            'start_at': at(2026, 5, 17, 9),
            'end_at': at(2026, 5, 17, 12),
            'location': 'School Hall',
            'legacy_image_url': 'https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=600&h=300&fit=crop',
        },
        {
            'title': 'Annual Drama & Music Festival',
            'description': 'Students perform drama, choral music, and solo pieces celebrating the school’s artistic culture.',
            'category': 'culture',
            'start_at': at(2026, 6, 6, 14),
            'end_at': at(2026, 6, 6, 18),
            'location': 'School Auditorium',
            'legacy_image_url': 'https://images.unsplash.com/photo-1514320291840-2e0a9bf2a9ae?w=600&h=300&fit=crop',
        },
        {
            'title': 'School Open Day 2026',
            'description': 'Prospective parents and students tour the school, meet teachers, and learn about enrolment.',
            'category': 'academic',
            'start_at': at(2026, 6, 20, 9),
            'end_at': at(2026, 6, 20, 13),
            'location': 'Full School Campus',
            'legacy_image_url': 'https://images.unsplash.com/photo-1427504494785-3a9ca7044f45?w=600&h=300&fit=crop',
        },
        {
            'title': 'Annual Graduation Ceremony',
            'description': 'A joyful celebration honouring graduating Grade 6 students as they complete primary school.',
            'category': 'community',
            'start_at': at(2026, 7, 18, 10),
            'end_at': at(2026, 7, 18, 14),
            'location': 'School Hall',
            'legacy_image_url': 'https://images.unsplash.com/photo-1508780709619-79562169bc64?w=600&h=300&fit=crop',
        },
        {
            'title': 'Science & Innovation Fair',
            'description': 'A showcase of student science and innovation projects.',
            'category': 'academic',
            'start_at': at(2025, 10, 15),
            'legacy_image_url': 'https://images.unsplash.com/photo-1551854838-212c50b4c184?w=400&h=400&fit=crop',
        },
        {
            'title': 'Annual Sports Day',
            'description': 'The school community gathered for a day of sport and teamwork.',
            'category': 'sports',
            'start_at': at(2025, 8, 15),
            'legacy_image_url': 'https://images.unsplash.com/photo-1541829070764-84a7d30dd3f3?w=400&h=400&fit=crop',
        },
        {
            'title': 'Prize Giving Day',
            'description': 'Students were recognised for their achievements.',
            'category': 'community',
            'start_at': at(2025, 12, 5),
            'legacy_image_url': 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=400&h=400&fit=crop',
        },
        {
            'title': 'Christmas Carol Concert',
            'description': 'The school community celebrated Christmas through music.',
            'category': 'culture',
            'start_at': at(2025, 12, 12),
            'legacy_image_url': 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=400&h=400&fit=crop',
        },
    ]
    for event in events:
        Event.objects.get_or_create(
            title=event['title'],
            start_at=event['start_at'],
            defaults=event,
        )


def remove_imported_events(apps, schema_editor):
    Event = apps.get_model('public', 'Event')
    titles = [
        'End of Term Examination Week',
        'Inter-School Athletics Day',
        'PTA Mid-Year Meeting',
        'Annual Drama & Music Festival',
        'School Open Day 2026',
        'Annual Graduation Ceremony',
        'Science & Innovation Fair',
        'Annual Sports Day',
        'Prize Giving Day',
        'Christmas Carol Concert',
    ]
    Event.objects.filter(title__in=titles).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0006_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='legacy_image_url',
            field=models.URLField(blank=True, editable=False),
        ),
        migrations.RunPython(import_existing_events, remove_imported_events),
    ]
