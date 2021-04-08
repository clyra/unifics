"""
add something useful here
"""

from datetime import timedelta
import voluptuous as vol
import async_timeout
import logging
from homeassistant import config_entries, core
from homeassistant.core import callback
from typing import Any, Callable, Dict, Optional
from unificontrol import UnifiClient
from .api_wrapper import create_client

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as config_validation
from homeassistant.const import (
    STATE_UNKNOWN, PRECISION_WHOLE
)
from .const import (
    CONF_NAME, CONF_USERNAME, CONF_PASSWORD, 
    CONF_HOST, CONF_PORT, CONF_SITE, CONF_VERIFY_SSL,
    CONF_UDM, DOMAIN
)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default='unifics'): config_validation.string,
        vol.Optional(CONF_USERNAME, default='admin'): config_validation.string,
        vol.Required(CONF_PASSWORD): config_validation.string,
        vol.Required(CONF_HOST): config_validation.string,
        vol.Optional(CONF_PORT, default=8443): config_validation.positive_int,
        vol.Optional(CONF_SITE, default='default'): config_validation.string,   
        vol.Optional(CONF_VERIFY_SSL, default=False): config_validation.boolean,
        vol.Optional(CONF_UDM, default=False): config_validation.boolean
    }
)

async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""
  
    config = hass.data[DOMAIN][config_entry.entry_id]
   
    def sync_create_client():
        return create_client(host=config.get(CONF_HOST), 
                             port=config.get(CONF_PORT), 
                             username=config.get(CONF_USERNAME),
                             password=config.get(CONF_PASSWORD), 
                             site=config.get(CONF_SITE),
                             cert=config.get(CONF_VERIFY_SSL),
                             udm=config.get(CONF_UDM)
                            )
    api = await hass.async_add_executor_job(sync_create_client)

    if api['error'] == 'ok':
        control = api['client']
        async def async_update_data():
            """ fetch data from the unifi wrapper"""
            async with async_timeout.timeout(10):
                data = await hass.async_add_executor_job(control.list_devices)
                return data

        coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name="sensor",
            update_method=async_update_data,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=30),
           )

        # Fetch initial data so we have data when entities subscribe
        await coordinator.async_refresh()

        entities = []
        entities.append(UnifiSensor(coordinator, config.get(CONF_NAME)))

        async_add_entities(entities)
    else:
        _LOGGER.error('Error while setting the sensor: {}'.format(api['error']))

async def async_setup_platform(
        hass: HomeAssistantType,
        config: ConfigType, 
        async_add_entities: Callable, 
        discovery_info: Optional[DiscoveryInfoType] = None):
    """Setup the unifi counter sensor."""

    def sync_create_client():
        return create_client(host=config.get(CONF_HOST), 
                             port=config.get(CONF_PORT), 
                             username=config.get(CONF_USERNAME),
                             password=config.get(CONF_PASSWORD), 
                             site=config.get(CONF_SITE),
                             cert=config.get(CONF_VERIFY_SSL),
                             udm=config.get(CONF_UDM)
                            )
    api = await hass.async_add_executor_job(sync_create_client)
    
    if api['error'] == 'ok':
        control = api['client']
        async def async_update_data():
            """ fetch data from the unifi wrapper"""
            async with async_timeout.timeout(10):
                data = await hass.async_add_executor_job(control.list_devices)
                return data

        coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name="sensor",
            update_method=async_update_data,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=30),
           )

        # Fetch initial data so we have data when entities subscribe
        await coordinator.async_refresh()

        entities = []
        entities.append(UnifiSensor(coordinator, config.get(CONF_NAME)))

        async_add_entities(entities)
    else:
        _LOGGER.error('Error while setting the sensor: {}'.format(api['error']))

class UnifiSensor(Entity):
    """Representation of a Unifi Sensor."""

    def __init__(self, coordinator, sensor_name):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._last_updated = None
        self._name = sensor_name
        self._unit = 'devices'
        self.ap_list = {}
        self._total = 0
        self._attr = {}


    def update_all(self):
        try:
            tmplist = self.coordinator.data

            total = 0
            self.ap_list = {}
            essid_sum = {}

            for ap in tmplist:
                if 'name' in ap.keys():
                    self.ap_list[ap['mac']] = { 'name': "AP " + ap['name'] }
                else:
                    self.ap_list[ap['mac']] = { 'name': "AP " + ap['mac'] }
                self.ap_list[ap['mac']]['num_sta'] = ap['num_sta']
                total += int(ap['num_sta'])
                self.ap_list[ap['mac']]['essidlist'] = []
                if 'vap_table' in ap.keys():
                  for i in ap['vap_table']:
                    self.ap_list[ap['mac']]['essidlist'].append( { 'essid': i['essid'], 
                                                               'channel': i['channel'], 
                                                               'num_sta': i['num_sta'] })
                    if i['essid'] in essid_sum.keys():
                        essid_sum[i['essid']] += int(i['num_sta'])
                    else:
                        essid_sum[i['essid']] = int(i['num_sta'])

            # add devieces per ap to the attr list
            for ap in self.ap_list.keys():
                self._attr[self.ap_list[ap]['name']] = self.ap_list[ap]['num_sta']

            # add devices per essid to attr list
            for k in essid_sum.keys():
                self._attr[k] = essid_sum[k]

            self._total = total

        except Exception as e:
            _LOGGER.error("Error while trying to update sensor: %s", e)
            self._total = 0

    def unifi_status(self, state):
        """ boiler status conversions """
        _LOGGER.debug(state)

        return self._total

    @property
    def should_poll(self):
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    @property
    def available(self):
        """Return if entity is available."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """When entity will be removed from hass."""
        self.coordinator.async_remove_listener(self.async_write_ha_state)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique ID of the binary sensor."""
        return f"{self._name}"

    #@property
    #def icon(self):
    #    """Icon to use in the frontend, if any."""
    #    return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        self.update_all()
        return self._total

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit

    @property
    def device_state_attributes(self):
        """Return the state attributes of this device."""
        #attr = {}
        #if self._last_updated is not None:
        #    attr["Last Updated"] = self._last_updated
        #return attr
        return self._attr

    async def async_update(self):
        """Update Entity
        Only used by the generic entity update service."""
        await self.coordinator.async_request_refresh()

