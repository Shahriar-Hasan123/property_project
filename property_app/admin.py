from django.contrib import admin
from django.contrib.gis import admin as gis_admin
from django.utils.html import format_html
from .models import Location, Property, PropertyImage


class PropertyImageInline(admin.TabularInline):
    """
    Shows property images directly inside the Property admin page.
    No need to go to a separate page to add images.
    """
    model = PropertyImage
    extra = 1  # Show 1 empty form by default
    readonly_fields = ["image_preview", "width", "height", "file_size"]
    fields = [
        "image",
        "image_preview",
        "alt_text",
        "caption",
        "is_primary",
        "sort_order",
    ]

    def image_preview(self, obj):
        """Shows a small thumbnail in the admin inline."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 80px; border-radius: 4px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"


@admin.register(Location)
class LocationAdmin(gis_admin.GISModelAdmin):
    """
    Admin for Location model.
    GISModelAdmin adds an interactive map widget for PointField.
    """
    list_display = [
        "name",
        "city",
        "state",
        "country",
        "is_active",
        "created_at",
    ]
    list_filter = ["country", "state", "is_active"]
    search_fields = ["name", "city", "state", "country", "address"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = [
        ("Basic Info", {
            "fields": ["name", "slug", "is_active"]
        }),
        ("Address", {
            "fields": ["country", "state", "city", "address"]
        }),
        ("GIS Data", {
            "fields": ["point", "boundary"],
            "classes": ["collapse"],  # Collapsible section
        }),
        ("AI Embedding", {
            "fields": ["embedding"],
            "classes": ["collapse"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]


@admin.register(Property)
class PropertyAdmin(gis_admin.GISModelAdmin):
    """
    Admin for Property model.
    Includes inline images and full filtering support.
    """
    list_display = [
        "title",
        "property_type",
        "status",
        "price",
        "bedrooms",
        "bathrooms",
        "location",
        "is_featured",
        "is_active",
        "created_at",
    ]
    list_filter = [
        "property_type",
        "status",
        "is_featured",
        "is_active",
        "location__country",
        "location__city",
    ]
    search_fields = ["title", "description", "address", "location__city"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["created_at", "updated_at"]
    inlines = [PropertyImageInline]

    fieldsets = [
        ("Basic Info", {
            "fields": [
                "location",
                "title",
                "slug",
                "description",
                "property_type",
                "status",
            ]
        }),
        ("Details", {
            "fields": [
                "price",
                "bedrooms",
                "bathrooms",
                "area_sqft",
                "address",
            ]
        }),
        ("Flags", {
            "fields": ["is_featured", "is_active"]
        }),
        ("GIS Data", {
            "fields": ["point", "footprint"],
            "classes": ["collapse"],
        }),
        ("AI Embedding", {
            "fields": ["embedding"],
            "classes": ["collapse"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    """
    Standalone admin for PropertyImage.
    Useful for bulk image management.
    """
    list_display = [
        "image_preview",
        "property",
        "is_primary",
        "sort_order",
        "created_at",
    ]
    list_filter = ["is_primary", "property__location__city"]
    search_fields = ["property__title", "alt_text", "caption"]
    readonly_fields = ["image_preview", "width", "height", "file_size", "created_at"]

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 60px; border-radius: 4px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"