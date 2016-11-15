
Intel Edison Software Library for 915MHz Explorer Block

This software is still in progress. Check back later

This software is released under the MIT license. See the accompanying
LICENSE.txt for more details.

# Pre-Requisites

The Explorer board libraries require a current version of MRAA to run. MRAA allows the Explorer software to control the Edison's input/output pins directly.

If you're running yocto, do the following:

    echo "src mraa-upm http://iotdk.intel.com/repos/3.0/intelgalactic/opkg/i586" > /etc/opkg/mraa-upm.conf
    opkg update
    opkg install mraa

If you're running ubilinux/jubilinux, follow the instructions here:
https://learn.sparkfun.com/tutorials/installing-libmraa-on-ubilinux-for-edison

# Setup


On your Intel Edison, run the following after connecting it to the internet:

    mkdir ~/src
    cd ~/src
    git clone https://github.com/EnhancedRadioDevices/915MHzEdisonExplorer_SW.git
    cd 915MHzEdisonExplorer_SW/spi_serial
    python setup.py install

# CC1110 Firmware

This software library is intended to work with a specific firmware variant on
the TI CC1110.

You can get that firmware from:
https://github.com/EnhancedRadioDevices/subg_rfspy

## Installing new firmware onto the CC1110

While the default firmware for the CC1110 should work well with this library,
there are cases where you'd want to change or update. To do that, please use
the ccprog library from @ps2.

https://github.com/ps2/ccprog

Once you've cloned and made that program, you can flash a new hex file to the CC1110 using the following commands:

    wget https://github.com/EnhancedRadioDevices/subg_rfspy/releases/download/v0.8-explorer/spi1_alt2_EDISON_EXPLORER_US_STDLOC.hex
    ccprog -p 19,7,36 erase
    ccprog -p 19,7,36 write spi1_alt2_EDISON_EXPLORER_US_STDLOC.hex

Note: the 19,7,36 numbers in the above string refer to the Edison hardware
pins that are used to communicate with the CC1110. If you aren't using the
Explorer board, you may need to use different pin numbers.

# Testing

Once you have the Explorer software and firmware loaded, you should be able to run the Explorer hardware test script to verify that everything is working. You can do this as follows:

    cd ~/src/915MHzEdisonExplorer_SW/
    python ExplorerTest.py
    
This should return an OK message and blink the two user LEDs on the Explorer board. If that happens, your board is working well.