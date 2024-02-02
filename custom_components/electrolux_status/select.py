"""Select platform for Electrolux Status."""
from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from pyelectroluxocp import OneAppApi

from .const import SELECT, DOMAIN
from .entity import ElectroluxEntity

import logging

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    appliances = coordinator.data.get('appliances', None)
    if appliances is not None:
        for appliance_id, appliance in appliances.appliances.items():
            entities = [entity for entity in appliance.entities if entity.entity_type == SELECT]
            _LOGGER.debug("Electrolux add %d selects to registry for appliance %s", len(entities), appliance_id)
            async_add_entities(entities)


class ElectroluxSelect(ElectroluxEntity, SelectEntity):
    """Electrolux Status binary_sensor class."""



    def __init__(self, coordinator: any, name: str, config_entry,
                 pnc_id: str, entity_type: str, entity_attr, entity_source, capability: dict[str, any], unit,
                 device_class: str, entity_category: EntityCategory,):
        super().__init__(coordinator=coordinator, capability=capability, name=name, config_entry=config_entry,
                         pnc_id=pnc_id, entity_type=entity_type, entity_attr=entity_attr, entity_source=entity_source,
                         unit=unit, device_class=device_class, entity_category=entity_category)
        values_dict: dict[str, any] | None = self.capability.get("values", None)
        self.options_list: dict[str, str] = {}
        for value in values_dict.keys():
            entry: dict[str, any] = values_dict[value]
            if "disabled" in entry.keys():
                continue
            label = value.replace("_", " ").title()
            self.options_list[label] = value

    # @property
    # def icon(self) -> str:
    #     """Return a representative icon."""
    #     if not self.available or self.current_option == "TODO":
    #         return "mdi:XXX"
    #     return "mdi:YYY"

    @property
    def current_option(self) -> str:
        value = self.extract_value()
        label = list(self.options_list.keys())[list(self.options_list.values()).index(value)]
        if label is None:
            return value
        return label

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        value = self.options_list[option]
        if value is None:
            return
        client: OneAppApi = self.api
        command: dict[str, any] = {}
        if self.entity_source:
            command = { self.entity_source: {self.entity_attr: value}}
        else:
            command = {self.entity_attr: value}
        _LOGGER.debug("Electrolux select option %s", command)
        result = await client.execute_appliance_command(self.pnc_id, command)
        _LOGGER.debug("Electrolux select option result %s", result)

    @property
    def options(self) -> list[str]:
        """Return a set of selectable options."""
        return list(self.options_list.keys())
        # return [TRANSLATABLE_POWER_OFF] + sorted(self._data.activity_names)
