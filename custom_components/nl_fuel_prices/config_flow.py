"""Config flow for Dutch Fuel Prices integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv

from .towns import get_town_options, get_town_coords, get_town_info

from .const import (
    DOMAIN,
    CONF_LOCATION_LAT,
    CONF_LOCATION_LON,
    CONF_RADIUS,
    CONF_FUEL_TYPE,
    CONF_UPDATE_INTERVAL,
    CONF_DAILY_NOTIFICATION,
    CONF_DAILY_NOTIFICATION_TIME,
    CONF_DAILY_NOTIFICATION_DAYS,
    CONF_NOTIFY_SERVICES,
    FUEL_TYPES,
    FUEL_EURO95,
    DEFAULT_RADIUS,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_DAILY_TIME,
    DEFAULT_DAILY_DAYS,
)


class FuelPricesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Dutch Fuel Prices."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Get coordinates from town selection or manual entry
            use_town = user_input.get("use_town_selector", True)
            
            if use_town and user_input.get("town"):
                coords = get_town_coords(user_input["town"])
                town_info = get_town_info(user_input["town"])
                if coords and town_info:
                    lat, lon = coords
                    location_name = user_input["town"]
                    # Store postcode info for display
                    user_input["town_postcode"] = town_info["postcode"]
                    user_input["town_province"] = town_info["province"]
                else:
                    errors["base"] = "invalid_town"
            else:
                # Manual coordinates
                try:
                    lat = float(user_input[CONF_LOCATION_LAT])
                    lon = float(user_input[CONF_LOCATION_LON])
                    location_name = user_input.get("location_name", "Custom")
                    
                    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                        errors["base"] = "invalid_coordinates"
                except (ValueError, KeyError):
                    errors["base"] = "invalid_coordinates"

            if not errors:
                await self.async_set_unique_id(
                    f"{DOMAIN}_{user_input[CONF_FUEL_TYPE]}_{location_name}"
                )
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=f"{FUEL_TYPES[user_input[CONF_FUEL_TYPE]]} - {location_name}",
                    data={
                        **user_input,
                        "location_name": location_name,
                        CONF_LOCATION_LAT: lat,
                        CONF_LOCATION_LON: lon,
                    },
                )

        # Get Home Assistant's home location as default
        home_lat = self.hass.config.latitude
        home_lon = self.hass.config.longitude
        
        # Get available notification services
        notify_services = self._get_notify_services()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Optional("use_town_selector", default=True): bool,
                vol.Optional("town"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=get_town_options(),
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional("location_name", default="Home"): str,
                vol.Optional(CONF_LOCATION_LAT, default=home_lat): cv.latitude,
                vol.Optional(CONF_LOCATION_LON, default=home_lon): cv.longitude,
                vol.Required(CONF_RADIUS, default=DEFAULT_RADIUS): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=50)
                ),
                vol.Required(CONF_FUEL_TYPE, default=FUEL_EURO95): vol.In(FUEL_TYPES),
                vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=5, max=60)
                ),
                vol.Optional(CONF_DAILY_NOTIFICATION, default=False): bool,
                vol.Optional(CONF_DAILY_NOTIFICATION_TIME, default=DEFAULT_DAILY_TIME): selector.TimeSelector(),
                vol.Optional(CONF_DAILY_NOTIFICATION_DAYS, default=DEFAULT_DAILY_DAYS): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"value": "mon", "label": "Monday"},
                            {"value": "tue", "label": "Tuesday"},
                            {"value": "wed", "label": "Wednesday"},
                            {"value": "thu", "label": "Thursday"},
                            {"value": "fri", "label": "Friday"},
                            {"value": "sat", "label": "Saturday"},
                            {"value": "sun", "label": "Sunday"},
                        ],
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(CONF_NOTIFY_SERVICES, default=[]): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=notify_services,
                        multiple=True,
                        custom_value=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }),
            errors=errors,
            description_placeholders={
                "town_help": "Select a Dutch town/city",
                "manual_help": "Or enter coordinates manually",
                "notify_help": "Select notification services (e.g., mobile_app_phone)",
            },
        )
    
    def _get_notify_services(self) -> list[dict[str, str]]:
        """Get available notification services."""
        services = []
        
        # Get all services in the notify domain
        try:
            if hasattr(self.hass, 'services') and self.hass.services:
                all_services = self.hass.services.async_services()
                if "notify" in all_services:
                    notify_services = all_services["notify"]
                    
                    for service_name in sorted(notify_services.keys()):
                        # Skip the generic notify service
                        if service_name == "notify":
                            continue
                            
                        services.append({
                            "value": service_name,
                            "label": service_name.replace("_", " ").title()
                        })
        except Exception:
            pass  # Silently fail and use defaults
        
        # Always add common ones (users can type custom values anyway)
        default_services = [
            {"value": "persistent_notification", "label": "Persistent Notification"},
            {"value": "mobile_app", "label": "Mobile App (Generic)"},
        ]
        
        # Add defaults that aren't already in the list
        existing_values = {s["value"] for s in services}
        for default in default_services:
            if default["value"] not in existing_values:
                services.insert(0, default)
        
        return services if services else default_services

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> FuelPricesOptionsFlow:
        """Get the options flow for this handler."""
        return FuelPricesOptionsFlow(config_entry)


class FuelPricesOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Dutch Fuel Prices."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Update config entry data
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={**self.config_entry.data, **user_input},
            )
            return self.async_create_entry(title="", data={})
        
        # Get available notification services
        notify_services = self._get_notify_services()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_RADIUS,
                    default=self.config_entry.data.get(CONF_RADIUS, DEFAULT_RADIUS),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=50)),
                vol.Required(
                    CONF_UPDATE_INTERVAL,
                    default=self.config_entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL),
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=60)),
                vol.Optional(
                    CONF_DAILY_NOTIFICATION,
                    default=self.config_entry.data.get(CONF_DAILY_NOTIFICATION, False),
                ): bool,
                vol.Optional(
                    CONF_DAILY_NOTIFICATION_TIME,
                    default=self.config_entry.data.get(CONF_DAILY_NOTIFICATION_TIME, DEFAULT_DAILY_TIME),
                ): selector.TimeSelector(),
                vol.Optional(
                    CONF_DAILY_NOTIFICATION_DAYS,
                    default=self.config_entry.data.get(CONF_DAILY_NOTIFICATION_DAYS, DEFAULT_DAILY_DAYS),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"value": "mon", "label": "Monday"},
                            {"value": "tue", "label": "Tuesday"},
                            {"value": "wed", "label": "Wednesday"},
                            {"value": "thu", "label": "Thursday"},
                            {"value": "fri", "label": "Friday"},
                            {"value": "sat", "label": "Saturday"},
                            {"value": "sun", "label": "Sunday"},
                        ],
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(
                    CONF_NOTIFY_SERVICES,
                    default=self.config_entry.data.get(CONF_NOTIFY_SERVICES, []),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=notify_services,
                        multiple=True,
                        custom_value=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }),
        )
    
    def _get_notify_services(self) -> list[dict[str, str]]:
        """Get available notification services."""
        services = []
        
        # Get all services in the notify domain
        try:
            if hasattr(self.hass, 'services') and self.hass.services:
                all_services = self.hass.services.async_services()
                if "notify" in all_services:
                    notify_services = all_services["notify"]
                    
                    for service_name in sorted(notify_services.keys()):
                        # Skip the generic notify service
                        if service_name == "notify":
                            continue
                            
                        services.append({
                            "value": service_name,
                            "label": service_name.replace("_", " ").title()
                        })
        except Exception:
            pass  # Silently fail and use defaults
        
        # Always add common ones (users can type custom values anyway)
        default_services = [
            {"value": "persistent_notification", "label": "Persistent Notification"},
            {"value": "mobile_app", "label": "Mobile App (Generic)"},
        ]
        
        # Add defaults that aren't already in the list
        existing_values = {s["value"] for s in services}
        for default in default_services:
            if default["value"] not in existing_values:
                services.insert(0, default)
        
        return services if services else default_services
