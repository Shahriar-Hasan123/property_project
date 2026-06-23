from django.core.management.base import BaseCommand
from sentence_transformers import SentenceTransformer
from property_app.models import Location


class Command(BaseCommand):
    """
    Generates and stores sentence embeddings for Locations.

    Usage:
        python manage.py generate_embeddings
    """

    help = "Generate embeddings for locations using all-MiniLM-L6-v2"

    def handle(self, *args, **options):
        self.stdout.write("Loading sentence transformer model...")

        model = SentenceTransformer("all-MiniLM-L6-v2")

        self.stdout.write(self.style.SUCCESS("Model loaded."))

        locations = Location.objects.filter(is_active=True)
        total = locations.count()

        if total == 0:
            self.stdout.write(self.style.WARNING("No locations found."))
            return

        self.stdout.write(f"\nGenerating embeddings for {total} locations...\n")

        for i, location in enumerate(locations, 1):
            # Build semantic text with location details, avoiding redundancy and None values
            parts = [location.name]
            
            # Add city only if it's different from name
            if location.city and location.city != location.name:
                parts.append(location.city)
            
            # Add state and country
            if location.state:
                parts.append(location.state)
            if location.country:
                parts.append(location.country)
            
            # Include description if available for richer semantic context
            if hasattr(location, 'description') and location.description:
                text = f"{', '.join(parts)}. {location.description}"
            else:
                text = ", ".join(parts)

            embedding = model.encode(text)
            location.embedding = embedding.tolist()
            location.save(update_fields=["embedding"])

            self.stdout.write(f"  [{i}/{total}] ✔ {location.name}")

        self.stdout.write(
            "\n"
            + "─" * 40
            + "\n"
            + self.style.SUCCESS(f"✔ Location embeddings done: {total}")
            + "\n"
            + "─" * 40
        )
