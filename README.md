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

## Installation & Setup

### Prerequisites

- Docker & Docker Compose installed ([Install Docker](https://docs.docker.com/get-docker/))

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd property_project
```

### Step 2: Create `.env` File

Create a `.env` file in the project root:

```env
USER_ID=1000
GROUP_ID=1000

SECRET_KEY=django-insecure-change-this-to-a-real-secret-key-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

DB_NAME=propertydb
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=postgres
DB_PORT=5432

MEDIA_URL=/media/
```

### Step 3: Build & Start Containers

```bash
docker compose build
docker compose up -d postgres
sleep 5
docker compose up -d django
```

### Step 4: Run Migrations

```bash
docker compose exec django python manage.py migrate
```

### Step 5: Create Superuser (Optional)

```bash
docker compose exec -it django python manage.py createsuperuser
```

### Access the Application

- **Django:** http://localhost:8000
- **Admin:** http://localhost:8000/admin
- **PostgreSQL:** localhost:5442

---

## Important Notes for Fresh Clones

**Always run on first clone:**
```bash
docker compose down -v
docker compose build
docker compose up -d postgres
sleep 5
docker compose up -d django
docker compose exec django python manage.py migrate
```

This ensures the `postgis` and `vector` extensions are created in a fresh database.

## Access the Application

- **Django Development Server:** http://localhost:8000
- **Django Admin:** http://localhost:8000/admin
- **PostgreSQL:** localhost:5442 (from host machine)

## Common Commands

```bash
# Start/stop containers
docker compose up -d
docker compose down

# Logs
docker compose logs -f django

# Database migrations
docker compose exec django python manage.py migrate
docker compose exec django python manage.py makemigrations

# Django shell
docker compose exec -it django python manage.py shell

# Create superuser
docker compose exec -it django python manage.py createsuperuser

# Access PostgreSQL
docker compose exec postgres psql -U postgres -d propertydb
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

| Issue | Solution |
|-------|----------|
| `permission denied` docker socket | `sudo usermod -aG docker $USER && newgrp docker` |
| Container logs | `docker compose logs <service-name>` |
| Full reset (clears DB) | `docker compose down -v && docker compose build && docker compose up -d` |
| Django migrations fail | Ensure PostgreSQL is healthy: `docker compose ps` |
| Changes not reflected | Restart container: `docker compose restart django` |

## Support

For issues or questions, please open an issue on GitHub.

## License

[Specify your license here]
