"""Config flow for Dutch Fuel Prices integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
import aiohttp

from homeassistant import config_entries
from homeassistant.core import callback, HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .geocoding import geocode_postcode, validate_dutch_postcode

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
    CONF_NOTIFY_ON_CHANGE,
    CONF_PRICE_DROP_THRESHOLD,
    CONF_PRICE_INCREASE_THRESHOLD,
    CONF_SCHEDULED_UPDATES,
    CONF_SCHEDULED_UPDATE_TIMES,
    FUEL_TYPES,
    FUEL_EURO95,
    DEFAULT_RADIUS,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_DAILY_TIME,
    DEFAULT_DAILY_DAYS,
    DEFAULT_PRICE_DROP_THRESHOLD,
    DEFAULT_PRICE_INCREASE_THRESHOLD,
    DEFAULT_SCHEDULED_UPDATE_TIMES,
)


def get_notify_services(hass: HomeAssistant | None) -> list[dict[str, str]]:
    """Get available notification services - shared function."""
    default_services = [
        {"value": "persistent_notification", "label": "Persistent Notification"},
        {"value": "mobile_app", "label": "Mobile App (Generic)"},
    ]
    
    if not hass:
        return default_services
    
    services = []
    
    try:
        if hasattr(hass, 'services') and hass.services:
            all_services = hass.services.async_services()
            
            # Check for telegram_bot service
            if "telegram_bot" in all_services:
                telegram_services = all_services["telegram_bot"]
                if "send_message" in telegram_services:
                    services.append({
                        "value": "telegram_bot",
                        "label": "📱 Telegram Bot (Direct)"
                    })
            
            # Check for notify services
            if "notify" in all_services:
                notify_services = all_services["notify"]
                
                for service_name in sorted(notify_services.keys()):
                    if service_name == "notify":
                        continue
                    
                    # Add icon for telegram notify service
                    if "telegram" in service_name.lower():
                        label = f"📱 {service_name.replace('_', ' ').title()}"
                    else:
                        label = service_name.replace("_", " ").title()
                        
                    services.append({
                        "value": service_name,
                        "label": label
                    })
    except Exception:
        return default_services
    
    existing_values = {s["value"] for s in services}
    for default in default_services:
        if default["value"] not in existing_values:
            services.insert(0, default)
    
    return services if services else default_services



class FuelPricesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Dutch Fuel Prices."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            postcode = user_input.get("postcode", "").strip().upper()
            
            if not validate_dutch_postcode(postcode):
                errors["postcode"] = "invalid_postcode"
            else:
                session = async_get_clientsession(self.hass)
                geo_result = await geocode_postcode(session, postcode)
                
                if not geo_result:
                    errors["postcode"] = "geocoding_failed"
                else:
                    lat = geo_result["latitude"]
                    lon = geo_result["longitude"]
                    city = geo_result.get("city", "Unknown")
                    province = geo_result.get("province", "")
                    
                    location_name = f"{postcode} ({city})"
                    
                    await self.async_set_unique_id(
                        f"{DOMAIN}_{user_input[CONF_FUEL_TYPE]}_{postcode}"
                    )
                    self._abort_if_unique_id_configured()
                    
                    return self.async_create_entry(
                        title=f"{FUEL_TYPES[user_input[CONF_FUEL_TYPE]]} - {location_name}",
                        data={
                            **user_input,
                            "postcode": postcode,
                            "location_name": location_name,
                            "city": city,
                            "province": province,
                            CONF_LOCATION_LAT: lat,
                            CONF_LOCATION_LON: lon,
                        },
                    )

        notify_services = get_notify_services(self.hass)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("postcode"): str,
                vol.Required(CONF_RADIUS, default=DEFAULT_RADIUS): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=50)
                ),
                vol.Required(CONF_FUEL_TYPE, default=FUEL_EURO95): vol.In(FUEL_TYPES),
                vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=5, max=60)
                ),
                vol.Optional(CONF_SCHEDULED_UPDATES, default=False): bool,
                vol.Optional(CONF_SCHEDULED_UPDATE_TIMES, default=DEFAULT_SCHEDULED_UPDATE_TIMES): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"value": "00:00:00", "label": "00:00 (Midnight)"},
                            {"value": "03:00:00", "label": "03:00 (3 AM)"},
                            {"value": "06:00:00", "label": "06:00 (6 AM)"},
                            {"value": "09:00:00", "label": "09:00 (9 AM)"},
                            {"value": "12:00:00", "label": "12:00 (Noon)"},
                            {"value": "15:00:00", "label": "15:00 (3 PM)"},
                            {"value": "18:00:00", "label": "18:00 (6 PM)"},
                            {"value": "21:00:00", "label": "21:00 (9 PM)"},
                        ],
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
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
                vol.Optional(CONF_NOTIFY_ON_CHANGE, default=False): bool,
                vol.Optional(CONF_PRICE_DROP_THRESHOLD, default=DEFAULT_PRICE_DROP_THRESHOLD): vol.All(
                    vol.Coerce(float), vol.Range(min=0.01, max=1.0)
                ),
                vol.Optional(CONF_PRICE_INCREASE_THRESHOLD, default=DEFAULT_PRICE_INCREASE_THRESHOLD): vol.All(
                    vol.Coerce(float), vol.Range(min=0.01, max=1.0)
                ),
            }),
            errors=errors,
            description_placeholders={
                "postcode_help": "Enter Dutch postcode (e.g. 1621AB for Hoorn)",
                "postcode_format": "Format: 1234AB (4 digits + 2 letters)",
                "notify_help": "Select notification services",
            },
        )
    
    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> FuelPricesOptionsFlow:
        """Get the options flow for this handler."""
        return FuelPricesOptionsFlow()


class FuelPricesOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Dutch Fuel Prices."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={**self.config_entry.data, **user_input},
            )
            return self.async_create_entry(title="", data={})
        
        notify_services = get_notify_services(self.hass)

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
                    CONF_SCHEDULED_UPDATES,
                    default=self.config_entry.data.get(CONF_SCHEDULED_UPDATES, False),
                ): bool,
                vol.Optional(
                    CONF_SCHEDULED_UPDATE_TIMES,
                    default=self.config_entry.data.get(CONF_SCHEDULED_UPDATE_TIMES, DEFAULT_SCHEDULED_UPDATE_TIMES),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"value": "00:00:00", "label": "00:00 (Midnight)"},
                            {"value": "03:00:00", "label": "03:00 (3 AM)"},
                            {"value": "06:00:00", "label": "06:00 (6 AM)"},
                            {"value": "09:00:00", "label": "09:00 (9 AM)"},
                            {"value": "12:00:00", "label": "12:00 (Noon)"},
                            {"value": "15:00:00", "label": "15:00 (3 PM)"},
                            {"value": "18:00:00", "label": "18:00 (6 PM)"},
                            {"value": "21:00:00", "label": "21:00 (9 PM)"},
                        ],
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
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
                vol.Optional(
                    CONF_NOTIFY_ON_CHANGE,
                    default=self.config_entry.data.get(CONF_NOTIFY_ON_CHANGE, False),
                ): bool,
                vol.Optional(
                    CONF_PRICE_DROP_THRESHOLD,
                    default=self.config_entry.data.get(CONF_PRICE_DROP_THRESHOLD, DEFAULT_PRICE_DROP_THRESHOLD),
                ): vol.All(vol.Coerce(float), vol.Range(min=0.01, max=1.0)),
                vol.Optional(
                    CONF_PRICE_INCREASE_THRESHOLD,
                    default=self.config_entry.data.get(CONF_PRICE_INCREASE_THRESHOLD, DEFAULT_PRICE_INCREASE_THRESHOLD),
                ): vol.All(vol.Coerce(float), vol.Range(min=0.01, max=1.0)),
            }),
        )
