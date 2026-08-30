from django.contrib import admin
from django.urls import path, include
from .views import dashboard_page

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [

    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "dashboard/",
        dashboard_page,
        name="dashboard"
    ),


    # Inventory APIs
    path(
        "api/",
        include("Inventary.urls")
    ),

    # Order Management
    path(
        "orders/",
        include("Ordermanagement.urls")
    ),

    # JWT Authentication
    path(
        "api/auth/token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair"
    ),

    path(
        "api/auth/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh"
    ),

    # OpenAPI Schema
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema"
    ),

    # Swagger
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema"
        ),
        name="swagger-ui"
    ),
]