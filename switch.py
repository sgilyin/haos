"""Support for StarLine switch."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .account import StarlineAccount, StarlineDevice
from .const import DOMAIN
from .entity import StarlineEntity


@dataclass
class StarlineRequiredKeysMixin:
    """Mixin for required keys."""

    name_: str
    icon_on: str
    icon_off: str


@dataclass
class StarlineSwitchEntityDescription(
    SwitchEntityDescription, StarlineRequiredKeysMixin
):
    """Describes Starline switch entity."""


SWITCH_TYPES: tuple[StarlineSwitchEntityDescription, ...] = (
    StarlineSwitchEntityDescription(
        key="ign",
        name_="Engine",
        icon_on="mdi:engine-outline",
        icon_off="mdi:engine-off-outline",
    ),
    StarlineSwitchEntityDescription(
        key="webasto",
        name_="Webasto",
        icon_on="mdi:radiator",
        icon_off="mdi:radiator-off",
    ),
    StarlineSwitchEntityDescription(
        key="out",
        name_="Additional Channel",
        icon_on="mdi:access-point-network",
        icon_off="mdi:access-point-network-off",
    ),
    StarlineSwitchEntityDescription(
        key="poke",
        name_="Horn",
        icon_on="mdi:bullhorn-outline",
        icon_off="mdi:bullhorn-outline",
    ),
    StarlineSwitchEntityDescription(
        key="flex_0",
        name_="Flex 0",
        icon_on="mdi:numeric-0-box-outline",
        icon_off="mdi:numeric-0-box-outline",
    ),
    StarlineSwitchEntityDescription(
        key="flex_1",
        name_="Flex 1",
        icon_on="mdi:numeric-1-box-outline",
        icon_off="mdi:numeric-1-box-outline",
    ),
    StarlineSwitchEntityDescription(
        key="flex_2",
        name_="Flex 2",
        icon_on="mdi:numeric-2-box-outline",
        icon_off="mdi:numeric-2-box-outline",
    ),
    StarlineSwitchEntityDescription(
        key="flex_3",
        name_="Flex 3",
        icon_on="mdi:numeric-3-box-outline",
        icon_off="mdi:numeric-3-box-outline",
    ),
    StarlineSwitchEntityDescription(
        key="flex_4",
        name_="Flex 4",
        icon_on="mdi:numeric-4-box-outline",
        icon_off="mdi:numeric-4-box-outline",
    ),
    StarlineSwitchEntityDescription(
        key="flex_5",
        name_="Flex 5",
        icon_on="mdi:numeric-5-box-outline",
        icon_off="mdi:numeric-5-box-outline",
    ),
    StarlineSwitchEntityDescription(
        key="flex_6",
        name_="Flex 6",
        icon_on="mdi:numeric-6-box-outline",
        icon_off="mdi:numeric-6-box-outline",
    ),
    StarlineSwitchEntityDescription(
        key="flex_7",
        name_="Flex 7",
        icon_on="mdi:numeric-7-box-outline",
        icon_off="mdi:numeric-7-box-outline",
    ),
    StarlineSwitchEntityDescription(
        key="flex_8",
        name_="Flex 8",
        icon_on="mdi:numeric-8-box-outline",
        icon_off="mdi:numeric-8-box-outline",
    ),
    StarlineSwitchEntityDescription(
        key="flex_9",
        name_="Flex 9",
        icon_on="mdi:numeric-9-box-outline",
        icon_off="mdi:numeric-9-box-outline",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the StarLine switch."""
    account: StarlineAccount = hass.data[DOMAIN][entry.entry_id]
    entities = [
        switch
        for device in account.api.devices.values()
        if device.support_state
        for description in SWITCH_TYPES
        if (switch := StarlineSwitch(account, device, description)).is_on is not None
    ]
    async_add_entities(entities)


class StarlineSwitch(StarlineEntity, SwitchEntity):
    """Representation of a StarLine switch."""

    entity_description: StarlineSwitchEntityDescription

    def __init__(
        self,
        account: StarlineAccount,
        device: StarlineDevice,
        description: StarlineSwitchEntityDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(account, device, description.key, description.name_)
        self.entity_description = description

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available and self._device.online

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the switch."""
        if self._key == "ign":
            return self._account.engine_attrs(self._device)
        return None

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return (
            self.entity_description.icon_on
            if self.is_on
            else self.entity_description.icon_off
        )

    @property
    def assumed_state(self):
        """Return True if unable to access real state of the entity."""
        return True

    @property
    def is_on(self):
        """Return True if entity is on."""
        if self._key == "poke" or self._key[0:5] == "flex_":
            return False
        return self._device.car_state.get(self._key)

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        self._account.api.set_car_state(self._device.device_id, self._key, True)

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        if self._key == "poke" or self._key[0:5] == "flex_":
            return
        self._account.api.set_car_state(self._device.device_id, self._key, False)
