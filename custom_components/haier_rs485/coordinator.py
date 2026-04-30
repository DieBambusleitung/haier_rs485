import asyncio
import logging
from datetime import timedelta
import PyHaier
from pymodbus.client import AsyncModbusTcpClient
from pymodbus import FramerType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

class HaierDataCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, ip_address, port):
        super().__init__(
            hass,
            _LOGGER,
            name="Haier WP Daten",
            update_interval=timedelta(seconds=15), # Alle 15 Sekunden abfragen
        )
        self.ip_address = ip_address
        self.port = port
        self.device_id = 17

    async def _async_update_data(self):
        """Holt die Daten asynchron vom Converter."""
        client = AsyncModbusTcpClient(
            self.ip_address, 
            port=self.port, 
            framer=FramerType.RTU
        )
        
        try:
            await client.connect()
            if not client.connected:
                raise UpdateFailed("Konnte keine Verbindung zum Converter herstellen.")

            data = {}

            # 1. Basis Register abfragen
            p_101 = await client.read_holding_registers(address=101, count=6, device_id=self.device_id)
            if not p_101.isError() and len(p_101.registers) == 6:
                data["state"] = PyHaier.GetState(p_101.registers)
                data["target_temp"] = PyHaier.GetCHTemp(p_101.registers)
                data["target_dhw"] = PyHaier.GetDHWTemp(p_101.registers)
            else:
                _LOGGER.warning("Fehler beim Lesen der 101er Register")

            await asyncio.sleep(0.3) # WICHTIG: Pause für den RS485 Bus

            # 2. Modus Register
            p_201 = await client.read_holding_registers(address=201, count=1, device_id=self.device_id)
            if not p_201.isError() and len(p_201.registers) == 1:
                data["mode"] = PyHaier.GetMode(p_201.registers)

            await asyncio.sleep(0.3)

            # 3. Live Sensoren
            p_141 = await client.read_holding_registers(address=141, count=16, device_id=self.device_id)
            if not p_141.isError() and len(p_141.registers) == 16:
                try: data["current_dhw"] = PyHaier.GetDHWCurTemp(p_141.registers)
                except: data["current_dhw"] = None
                
                try: 
                    twi, two = PyHaier.GetTwiTwo(p_141.registers)
                    data["twi"] = twi
                    data["two"] = two
                except: pass

            return data

        except Exception as err:
            raise UpdateFailed(f"Fehler bei der Kommunikation: {err}")
        finally:
            client.close()