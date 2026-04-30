import logging
import PyHaier
from pymodbus.client import AsyncModbusTcpClient
from pymodbus import FramerType

from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import UnitOfTemperature

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Fügt die Number-Entitäten zu Home Assistant hinzu."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        HaierTargetTempNumber(coordinator)
        #HaierTargetDHWNumber(coordinator)
    ])

class HaierTargetTempNumber(CoordinatorEntity, NumberEntity):
    """Schieberegler für das Soll Heizen/Kühlen."""
    
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_native_step = 0.5 # PyHaier unterstützt hier 0.5°C Schritte
    _attr_native_min_value = 25.0 # Anpassen an deine echten Minimal-Werte
    _attr_native_max_value = 55.0 # Anpassen an deine echten Maximal-Werte

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"haier_wp_target_temp_{coordinator.ip_address}"
        self._attr_name = "Soll Heizen/Kühlen"
        self._attr_icon = "mdi:thermometer-lines"

    @property
    def native_value(self):
        if not self.coordinator.data: return None
        return self.coordinator.data.get("target_temp")

    async def async_set_native_value(self, value: float) -> None:
        _LOGGER.info(f"Setze neue Zieltemperatur auf '{value}'...")
        client = AsyncModbusTcpClient(self.coordinator.ip_address, port=self.coordinator.port, framer=FramerType.RTU)
        try:
            await client.connect()
            payload = await client.read_holding_registers(address=101, count=6, device_id=self.coordinator.device_id)
            if payload.isError(): return
            
            # PyHaier berechnet den neuen Payload
            new_registers = PyHaier.SetCHTemp(payload.registers, float(value))
            
            await client.write_registers(address=101, values=new_registers, device_id=self.coordinator.device_id)
            await self.coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error(f"Fehler Zieltemperatur: {e}")
        finally:
            client.close()

# class HaierTargetDHWNumber(CoordinatorEntity, NumberEntity):
#     """Schieberegler für das Soll des Warmwassers (DHW)."""
    
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_native_step = 1.0 # PyHaier unterstützt beim DHW 1°C Schritte
#     _attr_native_min_value = 35.0
#     _attr_native_max_value = 60.0

#     def __init__(self, coordinator):
#         super().__init__(coordinator)
#         self._attr_unique_id = f"haier_wp_target_dhw_{coordinator.ip_address}"
#         self._attr_name = "Soll Warmwasser (DHW)"
#         self._attr_icon = "mdi:water-boiler"

#     @property
#     def native_value(self):
#         if not self.coordinator.data: return None
#         return self.coordinator.data.get("target_dhw")

#     async def async_set_native_value(self, value: float) -> None:
#         client = AsyncModbusTcpClient(self.coordinator.ip_address, port=self.coordinator.port, framer=FramerType.RTU)
#         try:
#             await client.connect()
#             payload = await client.read_holding_registers(address=101, count=6, device_id=self.coordinator.device_id)
#             if not payload.isError():
#                 new_registers = PyHaier.SetDHWTemp(payload.registers, float(value))
#                 await client.write_registers(address=101, values=new_registers, device_id=self.coordinator.device_id)
#                 await self.coordinator.async_request_refresh()
#         except Exception as e:
#             _LOGGER.error(f"Fehler DHW Zieltemperatur: {e}")
#         finally:
#             client.close()