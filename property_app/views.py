from django.shortcuts import render
from .models import Property, Location

# Create your views here.
def home(request):
    featured_properties = Property.objects.filter(is_featured=True, is_active=True).select_related("location").prefetch_related("images")[:6]
    total_properties = Property.objects.filter(is_active=True).count()
    total_locations = Location.objects.filter(is_active=True).count()

    property_types = [
        ("house", "House", "🏠"),
        ("apartment", "Apartment", "🏢"),
        ("villa", "Villa", "🏖️"),
        ("cabin", "Cabin", "🌲"),
        ("condo", "Condo", "🏙️"),
        ("cottage", "Cottage", "🌿"),
        ("studio", "Studio", "🛋️"),
        ("other", "Other", "🏡"),
    ]

    context = {
        "featured_properties": featured_properties,
        "total_properties": total_properties,
        "total_locations": total_locations,
        "property_types": property_types,
    }
    return render(request, "home.html", context)

def property_list(request):
    return render(request,"property_list.html")

def property_detail(request):
    return render(request, "property_detail.html")