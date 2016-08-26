#!/usr/bin/env python

import mraa as m
from time import sleep

def spi_xfer(cs, dev, b):
    tx = bytearray(1)
    #transfer a byte over spi
    tx[0] = (int('{:08b}'.format(b)[::-1], 2))
    print(format(tx[0], '02x'))
    cs.write(0)
    rxbuf = dev.write(tx)
    cs.write(1)
    return (int('{:08b}'.format(rxbuf[0])[::-1], 2))

dev = m.spiFromDesc("spi-raw-5-1")
#dev.lsbmode(True)
dev.frequency(62500)
#
# negative clk polarity
dev.mode(m.SPI_MODE0)
dev.bitPerWord(8)

rst_req = bytearray(3)
rst_req[0] = 0x99
rst_req[1] = 0x01
rst_req[2] = 0x07

version_req = bytearray(3)
version_req[0] = 0x99
version_req[1] = 0x01
version_req[2] = 0x02

txbuf = bytearray(16)

txbuf[0] = 0x99
txbuf[1] = 16
txbuf[2] = 1
txbuf[3] = 0
txbuf[4] = 0
txbuf[5] = 0
txbuf[6] = 0
txbuf[7] = 0
txbuf[8] = 0
txbuf[9] = 0
txbuf[10] = 0
txbuf[11] = 0
txbuf[12] = 0
txbuf[13] = 0
txbuf[14] = 0
txbuf[15] = 0

cs0 = m.Gpio(23)
cs0.dir(m.DIR_OUT)
cs0.write(1)

for x in range(1,2):
    print("getting state...")
    for y in range(0, len(rst_req)):
        rxbuf = spi_xfer(cs0, dev, rst_req[y])
        print("\trxbuf[" + str(y) + "] = " + format(rxbuf, '02x'))

    sleep(1)
    for y in range(0, len(version_req)):
            rxbuf = spi_xfer(cs0, dev, version_req[y])
            print("\trxbuf[" + str(y) + "] = " + format(rxbuf, '02x'))

    for y in range(0,len(txbuf)):
        rxbuf = spi_xfer(cs0, dev, txbuf[y])
        print("\trxbuf[" + str(y) + "] = " + format(rxbuf, '02x'))

