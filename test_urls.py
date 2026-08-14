from django.urls import include, path


urlpatterns = [
    path(
        "api/m01/",
        include(
            "backend.modules.M01_input_acquisition_validation.api.urls"
        ),
    ),
]