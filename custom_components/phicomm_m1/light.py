# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName:      phicomm_m1.py
# Author:        binss
# Create:        2018-08-25 16:12:25
# Description:   No Description
#


import logging
import datetime


from homeassistant.components.light import (
    ATTR_BRIGHTNESS, LightEntity, SUPPORT_BRIGHTNESS)

log = logging.getLogger(__name__)

SCAN_INTERVAL_SECONDS = 5
SCAN_INTERVAL = datetime.timedelta(seconds=SCAN_INTERVAL_SECONDS)
DEFAULT_NAME = 'Phicomm M1'
DOMAIN = 'phicomm_m1'


LOW_BRIGHTNESS = 0
HIGH_BRIGHTNESS = 128


def setup_platform(hass, config, add_devices, discovery_info=None):
    status = hass.data[DOMAIN]
    devs = [PhicommM1Brightness(status)]
    add_devices(devs)


class PhicommM1Brightness(LightEntity):
    """Representation of an m1 screen brightness."""

    def __init__(self, status, icon=None):
        """Initialize the switch."""
        self._state = False
        self._status = status
        self._icon = icon

    @property
    def should_poll(self):
        """Poll the plug."""
        return True

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_BRIGHTNESS

    @property
    def brightness(self):
        """Return the brightness of the light."""
        return self._status.brightness

    @property
    def name(self):
        """Return the name of the device if any."""
        return "M1 Brightness"

    @property
    def icon(self):
        """Return the icon to use for device if any."""
        return self._icon

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._status.target_brightness > 0

    def turn_on(self, **kwargs):
        """Turn the device on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS, HIGH_BRIGHTNESS)
        if brightness >= HIGH_BRIGHTNESS:
            self._status.target_brightness = 50
        elif brightness > LOW_BRIGHTNESS:
            self._status.target_brightness = 25
        else:
            self._status.target_brightness = 0

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self._status.target_brightness = 0
