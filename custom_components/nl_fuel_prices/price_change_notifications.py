"""Price change notification manager for Dutch Fuel Prices."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import (
    DOMAIN,
    CONF_NOTIFY_ON_CHANGE,
    CONF_NOTIFY_SERVICES,
    CONF_PRICE_DROP_THRESHOLD,
    CONF_PRICE_INCREASE_THRESHOLD,
    FUEL_TYPES,
)

_LOGGER = logging.getLogger(__name__)


class PriceChangeNotificationManager:
    """Manage price change notifications."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the price change notification manager."""
        self.hass = hass
        self._previous_prices: dict[str, float] = {}

    async def check_and_notify(
        self,
        entry: ConfigEntry,
        current_price: float,
        station_data: dict[str, Any],
    ) -> None:
        """Check for price changes and send notifications if thresholds are exceeded."""
        if not entry.data.get(CONF_NOTIFY_ON_CHANGE, False):
            return

        notify_services = entry.data.get(CONF_NOTIFY_SERVICES, [])
        if not notify_services:
            return

        entry_id = entry.entry_id
        previous_price = self._previous_prices.get(entry_id)

        if previous_price is None:
            self._previous_prices[entry_id] = current_price
            return

        price_change = current_price - previous_price

        drop_threshold = entry.data.get(CONF_PRICE_DROP_THRESHOLD, 0.03)
        increase_threshold = entry.data.get(CONF_PRICE_INCREASE_THRESHOLD, 0.03)

        fuel_type = entry.data.get("fuel_type", "euro95")
        fuel_name = FUEL_TYPES.get(fuel_type, fuel_type)
        location_name = entry.data.get("location_name", "Unknown")
        station_name = station_data.get("name", "Unknown")

        if price_change <= -drop_threshold:
            await self._send_notification(
                notify_services,
                "💚 Fuel Price Drop",
                f"{fuel_name} at {station_name} has dropped by €{abs(price_change):.3f}/L! "
                f"Now €{current_price:.3f}/L (was €{previous_price:.3f}/L). "
                f"Location: {location_name}",
            )
            _LOGGER.info(
                "Price dropped from €%.3f to €%.3f for %s",
                previous_price,
                current_price,
                entry_id,
            )

        elif price_change >= increase_threshold:
            await self._send_notification(
                notify_services,
                "📈 Fuel Price Increase",
                f"{fuel_name} at {station_name} has increased by €{price_change:.3f}/L. "
                f"Now €{current_price:.3f}/L (was €{previous_price:.3f}/L). "
                f"Location: {location_name}",
            )
            _LOGGER.info(
                "Price increased from €%.3f to €%.3f for %s",
                previous_price,
                current_price,
                entry_id,
            )

        self._previous_prices[entry_id] = current_price

    async def _send_notification(
        self,
        services: list[str],
        title: str,
        message: str,
    ) -> None:
        """Send notification to all configured services."""
        for service in services:
            try:
                await self.hass.services.async_call(
                    "notify",
                    service,
                    {
                        "title": title,
                        "message": message,
                    },
                    blocking=False,
                )
            except Exception as err:
                _LOGGER.error("Failed to send notification to %s: %s", service, err)

    def clear_price(self, entry_id: str) -> None:
        """Clear stored price for an entry."""
        self._previous_prices.pop(entry_id, None)
