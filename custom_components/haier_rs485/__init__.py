import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_IP_ADDRESS, CONF_PORT
from .coordinator import HaierDataCoordinator

_LOGGER = logging.getLogger(__name__)

# Diese Plattformen wollen wir laden (Sensoren, Dropdowns, Zahlen)
PLATFORMS = ["select", "sensor", "number"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Wird aufgerufen, wenn die Integration gestartet wird."""
    hass.data.setdefault(DOMAIN, {})

    # Verbindungsdaten aus dem Config Flow holen
    ip_address = entry.data[CONF_IP_ADDRESS]
    port = entry.data[CONF_PORT]

    # Unseren Coordinator initialisieren
    coordinator = HaierDataCoordinator(hass, ip_address, port)

    # Erster Datenabruf - schlägt dieser fehl, startet die Integration nicht
    await coordinator.async_config_entry_first_refresh()

    # Coordinator im Home Assistant Speicher ablegen, damit andere Dateien ihn nutzen können
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Die Plattformen (select.py, sensor.py etc.) laden
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Wird aufgerufen, wenn die Integration gelöscht oder neugestartet wird."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok