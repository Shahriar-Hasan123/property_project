# Property Project

A Django-based property management application with GeoDjango, PostgreSQL/PostGIS, and Docker support.

## Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development)
- PostgreSQL 17 with PostGIS extension

## Project Structure

```
property_project/
├── config/                 # Django configuration
│   ├── settings.py        # Main settings
│   ├── urls.py            # URL routing
│   ├── wsgi.py            # WSGI application
│   └── asgi.py            # ASGI application
├── property_app/          # Main Django app
│   ├── models.py          # Database models
│   ├── views.py           # Views
│   ├── admin.py           # Admin configuration
│   └── migrations/        # Database migrations
├── docker/                # Docker configuration
│   ├── Dockerfile.django  # Django container
│   └── Dockerfile.postgres # PostgreSQL container
├── templates/             # Django templates
├── static/                # Static files (CSS, JS, images)
├── media/                 # User-uploaded media
├── docker-compose.yml     # Docker Compose configuration
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── manage.py              # Django management script
└── db.sqlite3             # SQLite database (development only)
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd property_project
```

### 2. Create `.env` File

Copy the example environment variables:

```bash
cp .env.example .env  # or create manually
```

**`.env` file contents:**

```env
# User/Group IDs (for Docker file ownership)
USER_ID=1000
GROUP_ID=1000

# Django
SECRET_KEY=django-insecure-change-this-to-a-real-secret-key-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
DB_NAME=propertydb
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=postgres
DB_PORT=5432

# Media
MEDIA_URL=/media/
```

### 3. Build Docker Images

```bash
docker compose build
```

### 4. Run Containers

```bash
docker-compose up
```

**Note:** The `USER_ID` and `GROUP_ID` are already configured in `.env`, so no extra environment variables are needed!

### 5. Run Migrations (First Time Only)

In a new terminal:

```bash
docker exec property_django python manage.py migrate
```

### 6. Create Superuser (First Time Only)

```bash
docker exec -it property_django python manage.py createsuperuser
```

## Access the Application

- **Django Development Server:** http://localhost:8000
- **Django Admin:** http://localhost:8000/admin
- **PostgreSQL:** localhost:5442 (from host machine)

## Common Commands

```bash
# Build images
docker compose build

# Start containers
docker-compose up

# Stop containers
docker compose down

# View logs
docker compose logs -f django

# Run Django management commands
docker exec property_django python manage.py <command>

# Open Django shell
docker exec -it property_django python manage.py shell

# Create migrations
docker exec property_django python manage.py makemigrations

# Apply migrations
docker exec property_django python manage.py migrate

# Create superuser
docker exec -it property_django python manage.py createsuperuser

# Collect static files
docker exec property_django python manage.py collectstatic --noinput
```

## File Ownership Issues

If you encounter permission errors like `Operation not permitted` when running `chown`:

**The Issue:** Docker containers running as root create files owned by root, causing permission conflicts.

**The Solution:** The `docker-compose.yml` and `.env` are configured to run containers as your user:
- `USER_ID=1000` in `.env`
- `GROUP_ID=1000` in `.env`
- `user: "${USER_ID}:${GROUP_ID}"` in `docker-compose.yml`

Just run: `docker-compose up`

**If ownership is already wrong:**
```bash
# Fix with Docker (no sudo needed)
docker run --rm -v /path/to/property_project:/project alpine sh -c "chown -R 1000:1000 /project"
```

## Technologies Used

- **Django 5.1.4** - Web framework
- **PostgreSQL 17** - Database
- **PostGIS 3** - Spatial database extension
- **GeoDjango** - Django GIS framework
- **Django REST Framework** - API development
- **pgvector** - Vector database extension
- **Python 3.12** - Programming language

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `DEBUG` | Debug mode | `True` / `False` |
| `ALLOWED_HOSTS` | Allowed hostnames | `localhost,127.0.0.1,0.0.0.0` |
| `DB_NAME` | Database name | `propertydb` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `postgres` |
| `DB_HOST` | Database host | `postgres` |
| `DB_PORT` | Database port | `5432` |
| `MEDIA_URL` | Media files URL | `/media/` |

## Production Deployment

Before deploying to production:

1. Set `DEBUG=False` in `.env`
2. Generate a secure `SECRET_KEY`
3. Update `ALLOWED_HOSTS` with your domain
4. Use environment variables for sensitive data
5. Configure proper database backups
6. Set up HTTPS/SSL
7. Use a production WSGI server (Gunicorn, uWSGI)
8. Configure a reverse proxy (Nginx, Apache)

## Troubleshooting

### Containers not starting?
- Check logs: `docker compose logs`
- Ensure ports 5442 and 8000 are available
- Verify `.env` file exists

### Database connection errors?
- Ensure PostgreSQL container is healthy: `docker compose ps`
- Check database credentials in `.env`
- Wait for PostgreSQL to be ready before running migrations

### Permission denied errors?
- Always use: `USER_ID=$(id -u) GROUP_ID=$(id -g) docker-compose up`
- Fix existing files: `docker run --rm -v $PWD:/project alpine sh -c "chown -R 1000:1000 /project"`

## Support

For issues or questions, please open an issue on GitHub.

## License

[Specify your license here]
