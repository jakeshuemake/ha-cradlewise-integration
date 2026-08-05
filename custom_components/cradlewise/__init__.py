"""The Cradlewise Data API integration."""
from __future__ import annotations

from datetime import datetime, timedelta
import urllib.parse

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    BASE_URL,
    CONF_API_TOKEN,
    DOMAIN,
    LOGGER,
    SCAN_INTERVAL_METRICS,
    SCAN_INTERVAL_STATUS,
)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Cradlewise from a config entry."""
    token = entry.data[CONF_API_TOKEN]
    headers = {"Authorization": f"Bearer {token}"}
    session = async_get_clientsession(hass)

    async def async_update_status():
        """Fetch real-time status data."""
        try:
            async with session.get(f"{BASE_URL}/baby/status", headers=headers, timeout=10) as resp:
                if resp.status in (401, 403):
                    raise ConfigEntryAuthFailed("Token expired or Nurture Plus inactive")
                elif resp.status == 429:
                    LOGGER.warning("Cradlewise API rate limit hit (429). Waiting for next cycle.")
                    raise UpdateFailed("Rate limited on status endpoint")
                elif resp.status != 200:
                    raise UpdateFailed(f"HTTP Error {resp.status}")
                return await resp.json()
        except ConfigEntryAuthFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"Status update error: {err}") from err

    async def async_update_metrics():
        """Fetch historical sleep metrics formatted with space-separated datetimes."""
        now = datetime.now()
        start = now - timedelta(days=1)
        
        start_str = urllib.parse.quote(start.strftime("%Y-%m-%d %H:%M:%S"))
        end_str = urllib.parse.quote(now.strftime("%Y-%m-%d %H:%M:%S"))

        c_chart_url = f"{BASE_URL}/sleep/c-chart?start_time={start_str}&end_time={end_str}"
        day_metrics_url = f"{BASE_URL}/sleep/day-metrics?start_time={start_str}&end_time={end_str}"

        try:
            metrics_data = {}
            
            async with session.get(c_chart_url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    metrics_data["c_chart"] = await resp.json()
            
            async with session.get(day_metrics_url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    metrics_data["day_metrics"] = await resp.json()

            return metrics_data
        except Exception as err:
            raise UpdateFailed(f"Metrics update error: {err}") from err

    status_coordinator = DataUpdateCoordinator(
        hass,
        LOGGER,
        name="cradlewise_status",
        update_method=async_update_status,
        update_interval=SCAN_INTERVAL_STATUS,
    )

    metrics_coordinator = DataUpdateCoordinator(
        hass,
        LOGGER,
        name="cradlewise_metrics",
        update_method=async_update_metrics,
        update_interval=SCAN_INTERVAL_METRICS,
    )

    await status_coordinator.async_config_entry_first_refresh()
    await metrics_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "status": status_coordinator,
        "metrics": metrics_coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
