from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("properties/", views.property_list, name="property_list"),       # Feature 7
    path("properties/<slug:slug>/", views.property_detail, name="property_detail"),  # Feature 9
]