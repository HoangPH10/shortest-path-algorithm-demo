"""Configuration and environment variable management."""

import os
from typing import Optional

from dotenv import load_dotenv


def load_user_agent() -> str:
    """Load OpenStreetMap user agent from environment variables.

    Returns:
        User agent string for OSM API requests

    Note:
        Falls back to default if OSM_USER_AGENT is not set
    """
    load_dotenv()
    user_agent = os.getenv("OSM_USER_AGENT", "RoutePathfindingVisualizer/0.1.0")
    return user_agent


def get_osrm_server() -> str:
    """Get OSRM server URL from environment variables.

    Returns:
        OSRM server URL

    Note:
        Falls back to public OSRM server if OSRM_SERVER is not set
    """
    load_dotenv()
    osrm_server = os.getenv("OSRM_SERVER", "http://router.project-osrm.org")
    return osrm_server
