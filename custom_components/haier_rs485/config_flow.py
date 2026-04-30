import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_IP_ADDRESS, CONF_PORT, CONF_DEVICE_NAME

# Das Schema definiert die Eingabefelder im UI
DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_DEVICE_NAME, default="Haier WP"): str,
    vol.Required(CONF_IP_ADDRESS): str,
    vol.Required(CONF_PORT, default=502): int,
})

class HaierConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Hier könnte man einen kurzen Ping/Connect Test einbauen
            # Für den Anfang akzeptieren wir die Eingabe direkt:
            return self.async_create_entry(
                title=user_input[CONF_DEVICE_NAME], 
                data=user_input
            )

        return self.async_show_form(
            step_id="user", 
            data_schema=DATA_SCHEMA, 
            errors=errors
        )