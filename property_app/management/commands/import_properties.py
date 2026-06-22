import pandas as pd
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.utils.text import slugify
from property_app.models import Location, Property


class Command(BaseCommand):
    """
    Management command to import properties from a CSV file.
    Usage:
        python manage.py import_properties
        python manage.py import_properties --file data/custom.csv
        python manage.py import_properties --clear
    """

    help = "Import vacation rental properties from a CSV file"

    def add_arguments(self, parser):
        """
        Adds optional command-line arguments.
        --file  : path to CSV file (default: data/properties.csv)
        --clear : delete all existing data before import
        """
        parser.add_argument(
            "--file",
            type=str,
            default="data/properties.csv",
            help="Path to the CSV file (default: data/properties.csv)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear all existing properties and locations before import",
        )

    def handle(self, *args, **options):
        """
        Main logic of the command.
        Django calls this method when the command runs.
        """
        file_path = options["file"]

        # Optional: Clear existing data 
        if options["clear"]:
            self.stdout.write(self.style.WARNING("Clearing existing data..."))
            Property.objects.all().delete()
            Location.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Cleared."))

        # Load CSV 
        self.stdout.write(f"Reading CSV from: {file_path}")

        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        # Clean column names
        df.columns = df.columns.str.strip()

        # Track counters 
        created_locations = 0
        created_properties = 0
        skipped = 0

        # Process each row 
        for index, row in df.iterrows():
            try:
                # Step 1: Get or create Location 
                location_slug = slugify(
                    f"{row['city']}-{row['state']}-{row['country']}"
                )

                location, loc_created = Location.objects.get_or_create(
                    slug=location_slug,
                    defaults={
                        "name": f"{row['city']}, {row['state']}",
                        "city": row["city"],
                        "state": row.get("state", ""),
                        "country": row["country"],
                        "point": (
                            Point(
                                float(row["longitude"]),
                                float(row["latitude"]),
                                srid=4326,
                            )
                            if pd.notna(row.get("latitude"))
                            and pd.notna(row.get("longitude"))
                            else None
                        ),
                    },
                )

                if loc_created:
                    created_locations += 1

                # Step 2: Build unique property slug 
                base_slug = slugify(row["title"])
                slug = base_slug
                counter = 1

                # If slug already exists, add a number: "villa-1", "villa-2"
                while Property.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                # Step 3: Create Property
                point = None
                if pd.notna(row.get("latitude")) and pd.notna(row.get("longitude")):
                    # Point(longitude, latitude) — note the order
                    point = Point(
                        float(row["longitude"]), float(row["latitude"]), srid=4326
                    )

                Property.objects.create(
                    location=location,
                    title=row["title"],
                    slug=slug,
                    description=row.get("description", ""),
                    property_type=row.get("property_type", "other"),
                    status=row.get("status", "available"),
                    price=row["price"],
                    bedrooms=int(row.get("bedrooms", 0)),
                    bathrooms=int(row.get("bathrooms", 0)),
                    area_sqft=(
                        row.get("area_sqft") if pd.notna(row.get("area_sqft")) else None
                    ),
                    address=row.get("address", ""),
                    point=point,
                )

                created_properties += 1

                #Progress indicator 
                self.stdout.write(f"  ✔ Imported: {row['title']}")

            except Exception as e:
                skipped += 1
                self.stdout.write(self.style.ERROR(f"  ✘ Row {index + 2} failed: {e}"))
                continue

        # ── Final Summary ──
        self.stdout.write("\n" + "─" * 40)
        self.stdout.write(
            self.style.SUCCESS(f"✔ Locations created : {created_locations}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"✔ Properties created: {created_properties}")
        )
        if skipped:
            self.stdout.write(self.style.WARNING(f"⚠ Rows skipped      : {skipped}"))
        self.stdout.write("─" * 40)
