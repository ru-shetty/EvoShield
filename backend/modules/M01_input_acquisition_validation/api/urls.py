"""
URL definitions for EvoShield Module 1.
"""

from .views import InputAcquisitionView


input_acquisition_view = InputAcquisitionView()


URL_PATTERNS = {
    "input-acquisition": input_acquisition_view,
}


def get_view(route_name: str):
    """
    Return the view associated with a route.
    """

    if route_name not in URL_PATTERNS:
        raise KeyError(
            f"Route not found: {route_name}"
        )

    return URL_PATTERNS[route_name]