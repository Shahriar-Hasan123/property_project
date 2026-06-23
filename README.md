# Property Project

A Django-based property management application with GeoDjango, PostgreSQL/PostGIS, pgvector for semantic search, and Docker support.

## Features

- **GeoDjango Integration**: Location-based queries and geographic data types
- **PostGIS**: Advanced geographic capabilities (points, polygons, boundaries)
- **pgvector**: Vector embeddings for semantic similarity search
- **Property Management**: Full CRUD operations for properties and locations
- **Media Management**: Image uploads with automatic metadata extraction
- **Docker**: Production-ready containerized setup

## Prerequisites

- Docker & Docker Compose
- Git

## Project Structure

```
property_project/
├── config/                          # Django configuration
│   ├── settings.py                 # Main settings
│   ├── urls.py                     # URL routing
│   ├── wsgi.py                     # WSGI application
│   └── asgi.py                     # ASGI application
├── property_app/                    # Main Django app
│   ├── models.py                   # Database models (Location, Property, PropertyImage)
│   ├── views.py                    # Views
│   ├── admin.py                    # Admin configuration
│   ├── management/
│   │   └── commands/
│   │       ├── import_properties.py    # CSV import command
│   │       └── generate_embeddings.py  # Embedding generation command
│   └── migrations/                 # Database migrations
├── docker/                          # Docker configuration
│   ├── Dockerfile.django           # Django container
│   ├── Dockerfile.postgres         # PostgreSQL/PostGIS/pgvector container
│   └── init-extensions.sql         # Database extensions initialization
├── data/                            # Sample data
│   └── properties.csv              # Sample properties dataset
├── templates/                       # Django templates
├── static/                          # Static files (CSS, JS, images)
├── media/                           # User-uploaded media
├── docker-compose.yml              # Docker Compose configuration
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (not in git)
├── .dockerignore                   # Docker build exclusions
├── manage.py                       # Django management script
└── README.md                       # This file
```

## Installation & Setup

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd property_project
```

### Step 2: Environment Configuration

The `.env` file is already configured. Review and update if needed:

```env
DEBUG=True
SECRET_KEY=django-insecure-change-this-to-a-real-secret-key-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

DB_NAME=propertydb
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

MEDIA_URL=/media/
```

### Step 3: Build & Start Containers

```bash
docker compose down -v    # Clean slate (optional on first run)
docker compose build      # Build images
docker compose up -d      # Start all services
```

Verify containers are running:
```bash
docker compose ps
```

### Step 4: Run Migrations

```bash
docker compose exec web python manage.py migrate
```

### Step 5: Create Superuser (Admin Account)

```bash
docker compose exec -it web python manage.py createsuperuser
```

Then access Django admin at: **http://localhost:8000/admin**

### Step 6: Load Sample CSV Data (Optional)

Import properties from the sample dataset:

```bash
docker compose exec web python manage.py import_properties --file data/properties.csv
```

### Step 7: Generate Embeddings (Optional)

Generate vector embeddings for semantic search:

```bash
# Generate all embeddings
docker compose exec web python manage.py generate_embeddings

# Generate only location embeddings
docker compose exec web python manage.py generate_embeddings --model locations

# Generate only property embeddings
docker compose exec web python manage.py generate_embeddings --model properties
```

## Services

### Web Service
- **Container**: `property_web`
- **URL**: http://localhost:8000
- **Command**: `python manage.py runserver 0.0.0.0:8000`

### Database Service
- **Container**: `property_db`
- **Host**: `db` (from within containers)
- **Port**: 5432
- **Image**: `postgis/postgis:16-3.4` (PostgreSQL 16 with PostGIS 3.4 and pgvector 0.7.4)

## Database Extensions

The database automatically initializes with:
- **postgis**: Geographic data types and functions
- **pgvector**: Vector similarity search (for embeddings)
- **uuid-ossp**: UUID generation

## Common Commands

```bash
# View logs
docker compose logs -f web      # Django logs
docker compose logs -f db       # Database logs

# Access Django shell
docker compose exec web python manage.py shell

# Access PostgreSQL CLI
docker compose exec db psql -U postgres -d propertydb

# Stop all services
docker compose down

# Stop and remove all volumes (clean slate)
docker compose down -v

# Rebuild specific service
docker compose build web
docker compose build db
```

## Django Management Commands

### Import Properties
```bash
docker compose exec web python manage.py import_properties --file data/properties.csv
```

### Generate Embeddings
```bash
docker compose exec web python manage.py generate_embeddings
```

### Create Superuser
```bash
docker compose exec -it web python manage.py createsuperuser
```

## API Endpoints

- `/admin/` - Django Admin Interface
- `/properties/` - Property list page
- `/properties/<slug>/` - Property detail page
- `/api/properties/` - Properties API (if implemented)

## Development

### Making Code Changes

Code changes are reflected immediately thanks to Docker volume mounts. Restart Django if needed:

```bash
docker compose restart web
```

### Database Schema Changes

After modifying models:

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

## Troubleshooting

### Database Container Won't Start
- Ensure port 5432 is not in use
- Clear the volume: `docker compose down -v`
- Restart: `docker compose up -d`

### Web Container Won't Connect to Database
- Ensure `DB_HOST=db` in `.env` (service name, not localhost)
- Check database health: `docker compose logs db`
- Verify network: `docker network ls`

### Permission Errors on Media Files
- Media directory permissions are set to 755 in the Dockerfile
- Ensure Docker is running with proper permissions

### Embeddings Generation Fails
- Ensure database has pgvector extension: `docker compose exec db psql -U postgres -d propertydb -c "SELECT * FROM pg_extension WHERE extname='vector'"`
- Check sentence-transformers is installed: `docker compose exec web pip list | grep sentence-transformers`

## Production Deployment

For production, update `.env`:

```env
DEBUG=False
SECRET_KEY=<generate-a-strong-secret-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

And use a production WSGI server (Gunicorn, uWSGI) instead of Django's dev server.

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
