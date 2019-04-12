# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName:      phicomm_m1.py
# Author:        binss
# Create:        2018-08-24 19:10:15
# Description:   No Description
#


import logging
import json
import re
import threading
import asyncio

from tornado.tcpserver import TCPServer
from tornado.iostream import StreamClosedError
from tornado.options import define, options
from tornado.ioloop import IOLoop, PeriodicCallback

from homeassistant.const import (
    CONF_NAME, EVENT_HOMEASSISTANT_START, EVENT_HOMEASSISTANT_STOP)
from homeassistant.helpers import discovery


log = logging.getLogger(__name__)

SCAN_INTERVAL_SECONDS = 5
DOMAIN = 'phicomm_m1'


def setup(hass, config):
    log.info("Init phicommm M1 component")
    hass.data[DOMAIN] = PhicommM1Status()
    for component in ['sensor', 'light']:
        discovery.load_platform(hass, component, DOMAIN, {}, config)

    t = threading.Thread(target=run_m1_server, args=(hass.data[DOMAIN],))
    t.start()
    return True


def run_m1_server(status):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    server = PhicommM1Server(status)
    server.listen(9000)
    log.info("Starting server on tcp://0.0.0.0:9000")
    PeriodicCallback(server.update, SCAN_INTERVAL_SECONDS * 1000).start()
    IOLoop.instance().start()


class PhicommM1Status():

    def __init__(self):
        self._state = {}
        self._brightness = -1
        self._target_brightness = 0
        self._interval = SCAN_INTERVAL_SECONDS

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, val):
        self._state = val or {}

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, val):
        self._brightness = val

    @property
    def target_brightness(self):
        return self._target_brightness

    @target_brightness.setter
    def target_brightness(self, val):
        self._target_brightness = val

    @property
    def pm25(self):
        return self._state.get("value", 0)

    @property
    def hcho(self):
        return self._state.get("hcho", 0)

    @property
    def temperature(self):
        return self._state.get("temperature", 0)

    @property
    def humidity(self):
        return self._state.get("humidity", 0)


class PhicommM1Server(TCPServer):

    def __init__(self, status=None, hass=None, io_loop=None, ssl_options=None, **kwargs):
        # logger.debug('tcp server started')
        self.clients = {}
        self._status = status
        self._hass = hass
        TCPServer.__init__(
            self, ssl_options=ssl_options, **kwargs
        )

    async def handle_stream(self, stream, address):
        ip, fileno = address
        log.info("Incoming connection from " + ip)
        self.clients[fileno] = {'ip': ip, 'status': 0, 'stream': stream}

        while True:
            try:
                data = await stream.read_until('#END#'.encode("utf-8"))
                self._status.state = self.parse_data(data)
                # log.info(self._status.state)
            except StreamClosedError:
                if self.clients.get(fileno):
                    log.info("Client " + self.clients[fileno]['ip'] + " left.")
                    del self.clients[fileno]
                    break

    def parse_data(self, data):
        pattern = r"(\{.*?\})"
        json_str = re.findall(pattern, str(data), re.M)
        if len(json_str) > 0:
            return json.loads(json_str[-1])
        else:
            return {}

    def heartbeat(self):
        # log.info("ping")
        for fileno, client in self.clients.items():
            data = b'\xaa\xef\x012\xeb\x119\x8f\x0b\x00\x00\x00\x00\x00\x00\x00\x00\xb0\xf8\x93\x11\xbe#\x007\x00\x00\x02{"type":5,"status":1}\xff#END#'
            try:
                stream = client['stream']
                stream.write(data)
            except StreamClosedError:
                if self.clients.get(fileno):
                    log.info("Client " + self.clients[fileno]['ip'] + " left.")
                    del self.clients[fileno]

    def change_brightness(self):
        for fileno, client in self.clients.items():
            data = b'\xaa\xef\x012\xeb\x119\x8f\x0b\x00\x00\x00\x00\x00\x00\x00\x00\xb0\xf8\x93\x11\xbe#\x007\x00\x00\x02{"brightness":"%d","type":2}\xff#END#' % self._status.target_brightness
            try:
                stream = client['stream']
                stream.write(data)
                self._status.brightness = self._status.target_brightness
            except StreamClosedError:
                if self.clients.get(fileno):
                    log.info("Client " + self.clients[fileno]['ip'] + " left.")
                    del self.clients[fileno]

    def update(self):
        if self._status.target_brightness != self._status.brightness:
            self.change_brightness()
        else:
            self.heartbeat()


if __name__ == "__main__":
    options.parse_command_line()
    server = PhicommM1Server()
    server.listen(options.port)
    print("Starting server on tcp://0.0.0.0:" + str(options.port))
    PeriodicCallback(server.heartbeat, 5000).start()
    IOLoop.instance().start()
