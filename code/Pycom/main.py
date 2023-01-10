#!/usr/bin/env python
#
# Copyright (c) 2020, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#

# See https://docs.pycom.io for more information regarding library specifics

import time
import pycom
from pycoproc_1 import Pycoproc
import machine
from network import LoRa
import socket
import ubinascii

from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE

import ubinascii
import ustruct
import cayenneLPP

pycom.heartbeat(False)
pycom.rgbled(0x0A0A08) # white

py = Pycoproc(Pycoproc.PYSENSE)

# Initialise LoRa in LORAWAN mode.
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

print("V2 LoRaWAN")
print("DevEUI: %s" % (ubinascii.hexlify(lora.mac()).decode('ascii')))

# create an OTAA authentication parameters, change them to the provided credentials
app_eui = ubinascii.unhexlify('0000000000000000')
app_key = ubinascii.unhexlify('7B6AE8B632481A53D5023A701DA20630')
#uncomment to use LoRaWAN application provided dev_eui
dev_eui = ubinascii.unhexlify('01B1D1419131B1B5')

###############################################

# join a network using OTAA (Over the Air Activation)
#uncomment below to use LoRaWAN application provided dev_eui
#lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)
lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0)

# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.5)
    print('Not yet joined...')

print('Joined')

###############################################

# Get temperature and humidity
si = SI7006A20(py)
temperature = si.temperature()
humidity = si.humidity()
print("Temperature : " + str(temperature) + "C")
print("Humidity    : " + str(humidity) + "%")

# Get light
lt = LTR329ALS01(py)
lux = lt.lux()
print("Light (Lux) : " + str(lux))

###############################################

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

# make the socket blocking
# (waits for the data to be sent and for the 2 receive windows to expire)
s.setblocking(True)

###############################################

# creating Cayenne LPP packet
lpp = cayenneLPP.CayenneLPP(size = 100, sock = s)


lpp.add_digital_input(True)

# Temperature
lpp.add_temperature(temperature)
print('Add data [Temperature]')

# Light
lpp.add_luminosity(lux)
print('Add data [Light]')

# Humidity
lpp.add_relative_humidity(humidity)
print('Add data [Humidity]')

# sending the packet via the socket
lpp.send(reset_payload = True)
print('Data sent')

time.sleep(0.1)
py.setup_sleep(5)
py.go_to_sleep()