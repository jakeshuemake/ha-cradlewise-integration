"""Constants for the Cradlewise Data API integration."""
from datetime import timedelta
import logging

LOGGER = logging.getLogger(__package__)

DOMAIN = "cradlewise"
BASE_URL = "https://integrations.cradlewise.com/api/v1"

# Polling intervals to respect API limits (2 req/min status, 60 req/hr metrics)
SCAN_INTERVAL_STATUS = timedelta(seconds=30)
SCAN_INTERVAL_METRICS = timedelta(hours=1)

CONF_API_TOKEN = "api_token"
