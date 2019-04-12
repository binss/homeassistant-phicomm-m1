

# homeassistant-phicomm-m1

A custom component for phicomm m1(悟空)。

## Why I write it

Phicomm m1 is an awesome device because it integrate with temperature / humidity / PM2.5 / HCHO sensor and have color LED. The most attractive thing is its price which is less than 100 CNY. This is why I decide to buy it instead of MIHOME sensors or SIEMENS SirAir.

The bad news is that the phicomm company appears to be closing down and may stop to support the APP of m1 (~斐讯老板带着小姨子跑路了~). So it is a good choice to add the device to the self-host homeassistant.

There are some similar plugins for m1 on the forum(e.g. hassbian). However, I found that they were not working properly and had some strange bugs. So I spend a weekend (The most time consuming part is RTFSC of homeassistant since it lack of correlative docs) to write a new one, homeassistant-phicomm-m1. It work fine and could expose status to Apple homekit perfectly.

## How to use it

Install tornado since it rely on tornado.tcpserver:

```
pip3 install tornado
```

Clone homeassistant-phicomm-m1 codes to appropriate path:

* If you are using HA 0.88+, clone the master branch
* Otherwise clone the old branch

Then add

```
phicomm_m1:
```

to configuration.yaml .

Poison m1 DNS resolving and make `aircat.phicomm.com` point to your homeassistant host. You could use dnsmasq on your router to do it:

```
address=/.aircat.phicomm.com/192.168.10.250
```

## How it work

The phicomm_m1 component is a TCP server which accept the connection from m1 and poll the m1 to get newest status every 5 seconds.

The sensor/phicomm_m1 component get the status from server and update homeassistant entity status.

The light/phicomm_m1 component allow user to control the brightness of m1 screen by communicating with server.

