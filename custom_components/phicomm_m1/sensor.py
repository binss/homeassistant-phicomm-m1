# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName:      phicomm_m1.py
# Author:        binss
# Create:        2018-08-24 19:10:15
# Description:   No Description
#


import logging
import datetime

from homeassistant.const import TEMP_CELSIUS
from homeassistant.components.homekit.const import DEVICE_CLASS_CO2
from homeassistant.helpers.entity import Entity

log = logging.getLogger(__name__)

SCAN_INTERVAL_SECONDS = 5
SCAN_INTERVAL = datetime.timedelta(seconds=SCAN_INTERVAL_SECONDS)
DEFAULT_NAME = 'Phicomm M1'
DOMAIN = 'phicomm_m1'


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Phicomm M1 sensor."""
    status = hass.data[DOMAIN]
    devs = [PhicommM1Temperature(status),
            PhicommM1Humidity(status),
            PhicommM1PM25(status),
            PhicommM1Hcho(status)]

    add_devices(devs)


class PhicommM1Temperature(Entity):

    def __init__(self, status):
        """Initialize the sensor."""
        self._state = None
        self._status = status

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'M1 Temperature'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._status.temperature

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS


class PhicommM1Humidity(Entity):

    def __init__(self, status):
        """Initialize the sensor."""
        self._state = None
        self._status = status

    @property
    def device_class(self):
        return "humidity"

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'M1 Humidity'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._status.humidity

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "%"


class PhicommM1PM25(Entity):

    def __init__(self, status):
        """Initialize the sensor."""
        self._state = None
        self._status = status

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'M1 PM2.5'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._status.pm25

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "mg/m³"


class PhicommM1Hcho(Entity):

    def __init__(self, status):
        """Initialize the sensor."""
        self._state = None
        self._status = status

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'M1 Hcho'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._status.hcho

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "μg/m³"

    @property
    def device_class(self):
        """Since homeassistant-homekit do not support hcho sensor,
        We set our class to co2 for being showed in homekit.
        """
        return DEVICE_CLASS_CO2
