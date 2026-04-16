# Lofty Creek Christian School Management System

A comprehensive Django-based school management system for **Lofty Creek Christian School**, Nairobi, Kenya. Built with Django 4.2, Tailwind CSS, and integrates with Africa's Talking SMS gateway for parent communication.

## Features

### Public Website
- **Homepage** - Hero section, quick links, school overview
- **About Us** - School history, mission, vision, values
- **Academics** - Curriculum details, grade levels (Playgroup to Grade 6)
- **Admissions** - Online application process
- **Events** - School calendar and upcoming events
- **Gallery** - Photo gallery of school activities
- **Resources** - Downloadable materials for parents
- **Contact** - Contact form and school information

### Admin Dashboard
- **Contact Management** - Manage Parents, Teachers, and Staff contacts
- **Contact Groups** - Organize contacts by grade, category, etc.
- **SMS Campaigns** - Send bulk SMS notifications to parents/staff
- **SMS Templates** - Reusable message templates with variables
- **Campaign Tracking** - Track delivery status and costs

### SMS Integration
- Africa's Talking API integration for SMS notifications
- Bulk messaging to individuals or groups
- Scheduled message delivery
- Delivery status tracking
- Template variable support: `{name}`, `{balance}`, `{date}`

## Tech Stack

- **Backend**: Django 4.2, Python 3.10+
- **Frontend**: Tailwind CSS, DaisyUI, Font Awesome
- **Database**: PostgreSQL (production), SQLite (development)
- **SMS**: Africa's Talking API
- **Task Queue**: Celery with Redis
- **Admin Theme**: Django Jazzmin

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL (optional for development)
- Africa's Talking account

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/OrandiBrian/lofty_creek.git
cd lofty_creek
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings:
#   - SECRET_KEY
#   - DEBUG=True
#   - AFRICASTALKING_API_KEY
#   - AFRICASTALKING_USERNAME
#   - DATABASE_URL (for PostgreSQL)
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Collect static files**
```bash
python manage.py collectstatic
```

8. **Run development server**
```bash
python manage.py runserver
```

Visit `http://localhost:8000` for the public site and `http://localhost:8000/admin` for the admin dashboard.

## Project Structure

```
LCCS/
├── config/              # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/                # Core app - contacts and models
│   ├── models.py        # Contact, ContactGroup, SMSTemplate
│   ├── views.py         # Public page views
│   └── admin.py         # Admin configuration
├── public/              # Public website pages
│   ├── views.py         # About, Academics, Admissions, etc.
│   ├── templates/       # Public page templates
│   └── urls.py
├── sms/                 # SMS management module
│   ├── models.py        # SMSCampaign, SMSMessage
│   ├── views.py         # SMS dashboard views
│   ├── services.py      # Africa's Talking integration
│   └── templates/        # SMS dashboard templates
├── templates/           # Base templates
├── static/              # Static files (CSS, images)
├── requirements.txt    # Python dependencies
└── manage.py
```

## SMS Variables

Templates support the following variables that get replaced at send time:

| Variable | Description |
|----------|-------------|
| `{name}` | Contact's name |
| `{date}` | Current date |
| `{balance}` | Fee balance |
| `{message}` | Custom message |

Example template:
```
Dear {name}, this is a reminder that the school fees balance of KES {balance} is due on {date}. Contact us for any queries.
```

## Deployment

### Production Setup

1. Set `DEBUG=False` in environment
2. Configure PostgreSQL database
3. Set up Celery with Redis for async SMS sending
4. Use Gunicorn as WSGI server:
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | Debug mode | No |
| `DATABASE_URL` | PostgreSQL connection string | No |
| `AFRICASTALKING_API_KEY` | Africa's Talking API key | Yes (for SMS) |
| `AFRICASTALKING_USERNAME` | Africa's Talking username | Yes (for SMS) |
| `REDIS_URL` | Redis connection for Celery | No |

## School Information

- **Name**: Lofty Creek Christian School
- **Location**: Along Wambaa road, 0.5km off Nairobi-Nakuru Highway at Muthiga's Munyua road
- **Address**: P.O BOX 1882-00502, Nairobi
- **Phone**: +2547-2911-8877
- **Email**: info@loftycreekchristianschool.org
- **Programs**: Playgroup (2-3 years), PP1 & PP2 (4-5 years), Grades 1-6

## License

This project is proprietary software for Lofty Creek Christian School.

## Contributing

Contact the school administration for contribution guidelines.
