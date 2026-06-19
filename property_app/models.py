from django.contrib.gis.db import models as gis_models
from django.db import models
from pgvector.django import VectorField, HnswIndex


class Location(models.Model):

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True)

    # PointField stores a single GPS coordinate (longitude, latitude)
    point = gis_models.PointField(geography=True, srid=4326, null=True, blank=True)
    
    # MultiPolygonField stores the boundary of the location (e.g. city boundary)
    boundary = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)

    # 384 dimensions = all-MiniLM-L6-v2 model output size
    embedding = VectorField(dimensions=384, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            HnswIndex(
                name="location_embedding_idx",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            )
        ]

    def __str__(self):
        return f"{self.name}, {self.city}, {self.country}"


class Property(models.Model):

    PROPERTY_TYPE_CHOICES = [
        ("house", "House"),
        ("apartment", "Apartment"),
        ("villa", "Villa"),
        ("cabin", "Cabin"),
        ("condo", "Condo"),
        ("cottage", "Cottage"),
        ("studio", "Studio"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("available", "Available"),
        ("booked", "Booked"),
        ("inactive", "Inactive"),
    ]

    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="properties"
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    property_type = models.CharField(
        max_length=50, choices=PROPERTY_TYPE_CHOICES, default="house"
    )
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default="available"
    )

    price = models.DecimalField(max_digits=14, decimal_places=2)
    bedrooms = models.PositiveSmallIntegerField(default=0)
    bathrooms = models.PositiveSmallIntegerField(default=0)
    area_sqft = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    address = models.TextField(blank=True)

    # GIS Fields
    # Exact GPS point of the property
    point = gis_models.PointField(geography=True, srid=4326, null=True, blank=True)
    # Polygon of the property's physical footprint
    footprint = gis_models.PolygonField(srid=4326, null=True, blank=True)

    # AI embedding for semantic search (Day 3)
    embedding = VectorField(dimensions=384, null=True, blank=True)

    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Properties"
        indexes = [
            HnswIndex(
                name="property_embedding_idx",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            )
        ]

    def __str__(self):
        return f"{self.title} — {self.location.city}"


class PropertyImage(models.Model):

    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="properties/%Y/%m/")
    alt_text = models.CharField(max_length=255, blank=True)
    caption = models.TextField(blank=True)

    # Auto-filled image metadata
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)

    # AI embedding for image similarity search (Day 3)
    embedding = VectorField(dimensions=384, null=True, blank=True)

    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "-created_at"]

    def __str__(self):
        return f"Image for {self.property.title}"
