import logging
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Fügt die Sensoren zu Home Assistant hinzu."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Wir erstellen eine Liste aller Sensoren, die wir im Coordinator definiert haben
    sensors = [
        HaierTemperatureSensor(coordinator, "current_dhw", "Warmwasser Ist-Temperatur", "mdi:water-thermometer"),
        HaierTemperatureSensor(coordinator, "twi", "Wasser Einlauf (Twi)", "mdi:pipe"),
        HaierTemperatureSensor(coordinator, "two", "Wasser Auslauf (Two)", "mdi:pipe-leak"),
    ]

    async_add_entities(sensors)

class HaierTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Repräsentiert einen einzelnen Temperatur-Sensor der Wärmepumpe."""

    # Diese Attribute sagen Home Assistant, dass es sich um einen Sensor
    # handelt, der Grad Celsius misst und in Graphen dargestellt werden soll.
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator, data_key, name, icon):
        """Initialisiert den Sensor."""
        super().__init__(coordinator)
        
        self.data_key = data_key
        self._attr_name = name
        self._attr_icon = icon
        
        # Eindeutige ID (z.B. haier_wp_current_dhw_192.168.1.100)
        self._attr_unique_id = f"haier_wp_{data_key}_{coordinator.ip_address}"

    @property
    def native_value(self):
        """Gibt den aktuellen Wert des Sensors zurück."""
        if not self.coordinator.data:
            return None
        
        # Greift einfach auf das Dictionary des Coordinators zu
        return self.coordinator.data.get(self.data_key)