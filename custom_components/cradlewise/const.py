"""Constants for the Cradlewise Data API integration."""
from datetime import timedelta
import logging

LOGGER = logging.getLogger(__package__)

DOMAIN = "cradlewise"
BASE_URL = "https://integrations.cradlewise.com/api/v1"

# 35 seconds gives a safety buffer under the 2 req/min rate limit
SCAN_INTERVAL_STATUS = timedelta(seconds=35)
SCAN_INTERVAL_METRICS = timedelta(hours=1)

CONF_API_TOKEN = "api_token"
