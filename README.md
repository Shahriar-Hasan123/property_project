# Property Project

A Django-based property management application with GeoDjango, PostgreSQL/PostGIS, pgvector for semantic search, and Docker support.

## Features

- **GeoDjango Integration**: Location-based queries and geographic data types
- **PostGIS**: Advanced geographic capabilities (points, polygons, boundaries)
- **pgvector + Sentence Transformers**: AI-powered semantic similarity search using all-MiniLM-L6-v2 embeddings
- **Semantic Location Autocomplete**: Hybrid keyword + semantic search for intelligent location discovery
- **HNSW Vector Indexing**: Optimized cosine distance similarity queries for fast embedding search
- **Property Management**: Full CRUD operations for properties and locations
- **Media Management**: Image uploads with automatic metadata extraction
- **Docker**: Production-ready containerized setup with CPU-only PyTorch optimization

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

Copy `.env.example` to `.env` and update if needed:

```bash
cp .env.example .env
```

Then review and modify the variables in `.env`:

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

### Step 7: Generate Embeddings (Required for Semantic Search)

Generate vector embeddings for locations to enable AI-powered autocomplete:

```bash
docker compose exec web python manage.py generate_embeddings
```

The embeddings use:
- **Model**: Sentence Transformers (all-MiniLM-L6-v2) - 384 dimensions
- **Text**: Location name + city + state + country + description
- **Storage**: pgvector (PostgreSQL vector extension)
- **Indexing**: HNSW for fast cosine similarity queries

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

## Semantic Location Search

### How It Works

The location autocomplete API combines two search strategies for intelligent results:

1. **Keyword Matching** (Priority):
   - Searches location name, city, state, country for exact/prefix matches
   - Returns matching results first

2. **Semantic Search** (Fallback):
   - Uses AI embeddings (Sentence Transformers) to understand search intent
   - Finds semantically similar locations even if keywords don't match
   - Example: "beach city" finds coastal locations

### Architecture

```
User Query
    ↓
Tokenization & Embedding (Sentence Transformers)
    ↓
┌─────────────────────────────────────────┐
│ 1. Keyword Search (name, city, state)   │ ← Fast, exact matches
└─────────────────────────────────────────┘
    ↓
    ├─ Results found? Return them
    └─ Need more? Continue to semantic search
         ↓
    ┌──────────────────────────────────────────┐
    │ 2. Cosine Distance (pgvector + HNSW)     │ ← Fast, semantic matches
    └──────────────────────────────────────────┘
    ↓
Combine & Deduplicate Results
    ↓
Return Top N Locations
```

### Query Example

```bash
# Semantic search for "beach"
curl "http://localhost:8000/api/locations/autocomplete/?q=beach&limit=5"

# Result: Returns coastal/island locations even if name doesn't contain "beach"
```

### Performance

- **Keyword matches**: ~1-5ms (database index)
- **HNSW vector search**: ~10-50ms (indexed embeddings)
- **Total response**: <100ms for typical queries

### Embeddings

Each location stores a 384-dimensional embedding containing:
- Location name
- City, state, country
- Optional description for richer context

HNSW index ensures fast cosine distance calculations (O(log n) complexity).

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

### Web Pages
- `/` - Homepage with featured properties
- `/properties/` - Property list with filters
- `/properties/<slug>/` - Property detail page

### APIs
- `/api/locations/autocomplete/?q=<query>&limit=5` - Semantic location autocomplete (hybrid keyword + semantic search)

## Development

### Docker Optimization

The Dockerfile installs CPU-only PyTorch before other dependencies to optimize build time:

```dockerfile
# Install CPU-only PyTorch FIRST
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

# Then install other dependencies (prevents CUDA torch download)
RUN pip install -r requirements.txt
```

**Benefits:**
- ✅ ~70% faster Docker builds (avoids 2GB+ CUDA libraries)
- ✅ Smaller image size (~300MB vs 2.5GB)
- ✅ Faster container startup
- ✅ Ideal for CPU-only deployments

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
- Verify Location objects have city/state/country data before generating embeddings
- Check disk space - embedding generation requires temporary memory for the model

## Production Deployment

For production, update `.env`:

```env
DEBUG=False
SECRET_KEY=<generate-a-strong-secret-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

And use a production WSGI server (Gunicorn, uWSGI) instead of Django's dev server.

## Implementation Details

### Semantic Search Stack

| Component | Purpose | Technology |
|-----------|---------|-----------|
| **Model** | Text to embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| **Storage** | Vector storage | pgvector (PostgreSQL extension) |
| **Indexing** | Fast similarity search | HNSW (Hierarchical Navigable Small World) |
| **Distance** | Similarity metric | Cosine Distance |
| **Search** | Hybrid retrieval | Keyword (prefix) + Semantic (vector) |

### Files Modified

- `property_app/models.py` - Added `embedding` VectorField with HNSW index to Location model
- `property_app/views.py` - Added `LocationAutocompleteAPIView` with hybrid search strategy
- `property_app/serializers.py` - Added `LocationAutocompleteSerializer` for API responses
- `property_app/management/commands/generate_embeddings.py` - Command to generate and store location embeddings
- `docker/Dockerfile.django` - Optimized PyTorch installation (CPU-only)
- `requirements.txt` - Added `sentence-transformers==3.3.1` and `pgvector==0.3.6`

### Key Features Implemented

✅ Sentence Transformers integration (all-MiniLM-L6-v2)  
✅ Location embeddings generation and storage  
✅ HNSW vector indexing for fast queries  
✅ Hybrid keyword + semantic search  
✅ REST API for semantic location autocomplete  
✅ Docker optimization (CPU-only PyTorch)  
✅ Enhanced embedding text generation (handles None, includes descriptions)  

### Access the Application

- **Django:** http://localhost:8000
- **Admin:** http://localhost:8000/admin
- **PostgreSQL:** localhost:5432

---

## Important Notes for Fresh Clones

**Always run on first clone:**
```bash
docker compose down -v
docker compose build
docker compose up -d
docker compose exec web python manage.py migrate
```
