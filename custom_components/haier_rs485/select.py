import logging
import PyHaier
from pymodbus.client import AsyncModbusTcpClient
from pymodbus import FramerType

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# --- MAPPINGS (Übersetzung zwischen UI und PyHaier) ---

# STATUS: Links steht das, was du in Home Assistant siehst.
# Rechts steht der Befehlscode, den PyHaier.SetState() erwartet.
STATUS_TO_CMD = {
    "Off": "off",
    "On": "on",
    "Cool": "C",
    "Heat": "H",
    "Tank": "T",
    "Cool+Tank": "CT",
    "Heat+Tank": "HT"
}
STATUS_OPTIONS = list(STATUS_TO_CMD.keys())

# MODUS: Wir zeigen "Silent" an, senden aber "quiet" (PyHaier Standard).
MODE_TO_CMD = {
    "Eco": "eco",
    "Silent": "quiet", 
    "Turbo": "turbo"
}
MODE_OPTIONS = list(MODE_TO_CMD.keys())


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Fügt die Select-Entitäten zu Home Assistant hinzu."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        HaierStatusSelect(coordinator),
        HaierModeSelect(coordinator)
    ])

class HaierStatusSelect(CoordinatorEntity, SelectEntity):
    """Repräsentiert das Status-Dropdown für die Wärmepumpe."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"haier_wp_status_{coordinator.ip_address}"
        self._attr_name = "Wärmepumpen Status"
        self._attr_icon = "mdi:power-settings"
        self._attr_options = STATUS_OPTIONS

    @property
    def current_option(self):
        """Liest den Status aus und mappt ihn robust auf unsere schöne UI-Liste."""
        raw_state = self.coordinator.data.get("state")
        if not raw_state: 
            return None
        
        # 1. Alles in Großbuchstaben umwandeln, um den Text einheitlich zu machen
        safe_state = str(raw_state).strip().upper()
        
        # 2. Ist die Anlage ausgeschaltet?
        # Egal ob PyHaier "OFF", "HEAT OFF", "COOL OFF" oder "TANK OFF" meldet -> UI zeigt "Off"
        if "OFF" in safe_state:
            return "Off"
            
        # 3. Wenn sie an ist, entfernen wir das " ON", um nur den Modus (z. B. "HEAT") zu behalten
        safe_state = safe_state.replace(" ON", "").strip()
        
        # 4. Jetzt mappen wir den verbleibenden String auf unsere UI-Optionen
        if safe_state in ["C", "COOL"]: 
            return "Cool"
        elif safe_state in ["H", "HEAT"]: 
            return "Heat"
        elif safe_state in ["T", "TANK", "DHW"]: 
            return "Tank"
        elif safe_state in ["CT", "COOL+TANK", "C+T", "COOL TANK"]: 
            return "Cool+Tank"
        elif safe_state in ["HT", "HEAT+TANK", "H+T", "HEAT TANK"]: 
            return "Heat+Tank"
            
        # 5. Fallback für unerwartete Werte
        _LOGGER.warning(f"Unbekannter WP-Status von PyHaier empfangen: '{raw_state}'")
        return None

    async def async_select_option(self, option: str) -> None:
        """Übersetzt die Auswahl zurück in den kurzen PyHaier Befehl."""
        cmd = STATUS_TO_CMD.get(option)
        if not cmd: return

        _LOGGER.info(f"Sende neuen Status '{option}' (Interner Befehl: '{cmd}')...")
        client = AsyncModbusTcpClient(self.coordinator.ip_address, port=self.coordinator.port, framer=FramerType.RTU)
        try:
            await client.connect()
            payload = await client.read_holding_registers(address=101, count=6, device_id=self.coordinator.device_id)
            if payload.isError(): return
            
            # Wir übergeben hier "cmd" (z.B. "H"), nicht das Wort "Heat"!
            new_registers = PyHaier.SetState(payload.registers, cmd)
            await client.write_registers(address=101, values=new_registers, device_id=self.coordinator.device_id)
            
            # UI direkt aktualisieren
            await self.coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error(f"Fehler beim Ändern des Status: {e}")
        finally:
            client.close()


class HaierModeSelect(CoordinatorEntity, SelectEntity):
    """Repräsentiert das Modus-Dropdown für die Wärmepumpe."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"haier_wp_mode_{coordinator.ip_address}"
        self._attr_name = "Wärmepumpen Modus"
        self._attr_icon = "mdi:cog-outline"
        self._attr_options = MODE_OPTIONS

    @property
    def current_option(self):
        """Liest den Modus aus und mappt ihn auf unsere schöne UI-Liste."""
        mode = self.coordinator.data.get("mode")
        if not mode: return None
        
        mode_lower = mode.strip().lower()
        if mode_lower in ["quiet", "silent"]:
            return "Silent"
        elif mode_lower == "eco":
            return "Eco"
        elif mode_lower == "turbo":
            return "Turbo"
        
        return None

    async def async_select_option(self, option: str) -> None:
        """Übersetzt die Auswahl zurück in den PyHaier Befehl."""
        cmd = MODE_TO_CMD.get(option)
        if not cmd: return

        _LOGGER.info(f"Sende neuen Modus '{option}' (Interner Befehl: '{cmd}')...")
        client = AsyncModbusTcpClient(self.coordinator.ip_address, port=self.coordinator.port, framer=FramerType.RTU)
        try:
            await client.connect()
            #THEORETICALLY NOT NEEDED
            payload = await client.read_holding_registers(address=201, count=1, device_id=self.coordinator.device_id)
            if payload.isError(): return
            
            new_registers = PyHaier.SetMode(cmd)
            await client.write_registers(address=201, values=new_registers, device_id=self.coordinator.device_id)
            
            await self.coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error(f"Fehler beim Ändern des Modus: {e}")
        finally:
            client.close()