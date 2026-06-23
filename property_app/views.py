from django.shortcuts import render
from .models import Property, Location
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.http import JsonResponse
from pgvector.django import CosineDistance
from sentence_transformers import SentenceTransformer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LocationAutocompleteSerializer

_embedding_model = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model


# Create your views here.
def home(request):
    featured_properties = (
        Property.objects.filter(is_featured=True, is_active=True)
        .select_related("location")
        .prefetch_related("images")[:6]
    )
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
    # Start with all active properties
    queryset = (
        Property.objects.filter(is_active=True)
        .select_related("location")
        .prefetch_related("images")
        .order_by("-created_at")
    )

    # Read filter values from URL
    search = request.GET.get("search", "").strip()
    property_type = request.GET.get("property_type", "").strip()
    bedrooms = request.GET.get("bedrooms", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    sort_by = request.GET.get("sort_by", "newest").strip()

    # Apply search filter
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(address__icontains=search)
            | Q(location__city__icontains=search)
            | Q(location__state__icontains=search)
            | Q(location__country__icontains=search)
        )

    # Apply property type filter
    if property_type:
        queryset = queryset.filter(property_type=property_type)

    # Apply bedrooms filter
    if bedrooms:
        try:
            queryset = queryset.filter(bedrooms__gte=int(bedrooms))
        except ValueError:
            pass

    # Apply price filters
    if min_price:
        try:
            queryset = queryset.filter(price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            queryset = queryset.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Apply sorting
    sort_options = {
        "newest": "-created_at",
        "oldest": "created_at",
        "price_asc": "price",
        "price_desc": "-price",
    }
    order_field = sort_options.get(sort_by, "-created_at")
    queryset = queryset.order_by(order_field)

    # Pagination
    # Show 9 properties per page (3x3 grid)
    paginator = Paginator(queryset, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Build active filters dict for template
    # Used to show "Active Filters" badges and keep filters
    # when paginating (preserve filters in pagination links)
    active_filters = {}
    if search:
        active_filters["search"] = search
    if property_type:
        active_filters["property_type"] = property_type
    if bedrooms:
        active_filters["bedrooms"] = bedrooms
    if min_price:
        active_filters["min_price"] = min_price
    if max_price:
        active_filters["max_price"] = max_price
    if sort_by and sort_by != "newest":
        active_filters["sort_by"] = sort_by

    # Build query string for pagination links
    # e.g. "search=Miami&property_type=villa"
    filter_params = "&".join(f"{k}={v}" for k, v in active_filters.items())

    context = {
        "page_obj": page_obj,
        "total_count": paginator.count,
        "search": search,
        "property_type": property_type,
        "bedrooms": bedrooms,
        "min_price": min_price,
        "max_price": max_price,
        "sort_by": sort_by,
        "active_filters": active_filters,
        "filter_params": filter_params,
        "property_type_choices": Property.PROPERTY_TYPE_CHOICES,
    }
    return render(request, "property_list.html", context)


def property_detail(request, slug):

    property = get_object_or_404(
        Property.objects.select_related("location").prefetch_related("images"),
        slug=slug,
        is_active=True,
    )

    # Calculate distance from city center
    distance_from_city = None

    if property.point and property.location.point:
        property_with_distance = (
            Property.objects.filter(pk=property.pk)
            .annotate(distance=Distance("point", property.location.point))
            .first()
        )

        if property_with_distance:
            # .m gives distance in meters → convert to km
            distance_km = property_with_distance.distance.m / 1000
            distance_from_city = round(distance_km, 2)

    # Get all images
    images = property.images.all().order_by("sort_order", "-is_primary")
    primary_image = images.filter(is_primary=True).first() or images.first()

    context = {
        "property": property,
        "images": images,
        "primary_image": primary_image,
        "distance_from_city": distance_from_city,
    }
    return render(request, "property_detail.html", context)


class LocationAutocompleteAPIView(APIView):
    """
    Semantic location autocomplete API using DRF.
    Returns top matching locations based on meaning.

    GET /api/locations/autocomplete/?q=beachside city
    GET /api/locations/autocomplete/?q=mountain&limit=5
    
    """

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        limit = request.query_params.get("limit", 5)

        # Validate limit
        try:
            limit = min(int(limit), 10)
        except ValueError:
            limit = 5

        if len(query) < 2:
            return Response({"results": []})

        try:
            # First, try keyword-based matching for exact/prefix matches
            keyword_matches = Location.objects.filter(
                is_active=True,
                embedding__isnull=False,
            ).filter(
                Q(name__icontains=query)
                | Q(city__icontains=query)
                | Q(state__icontains=query)
                | Q(country__icontains=query)
            ).distinct()

            # Then get semantic results
            model = get_embedding_model()
            query_embedding = model.encode(query).tolist()

            semantic_matches = Location.objects.filter(
                is_active=True, embedding__isnull=False
            ).order_by(CosineDistance("embedding", query_embedding))

            # Combine results: keyword matches first, then semantic matches (avoiding duplicates)
            keyword_ids = set(keyword_matches.values_list("id", flat=True))
            combined_results = list(keyword_matches[:limit])

            # Fill remaining slots with semantic results (that aren't already in keyword matches)
            remaining_slots = limit - len(combined_results)
            if remaining_slots > 0:
                semantic_only = [
                    loc for loc in semantic_matches if loc.id not in keyword_ids
                ][:remaining_slots]
                combined_results.extend(semantic_only)

            serializer = LocationAutocompleteSerializer(combined_results, many=True)
            return Response({"results": serializer.data})

        except Exception as e:
            return Response(
                {"error": str(e), "results": []},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
