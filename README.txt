
Intel Edison Software Library for 915MHz Explorer Block

This software is still in progress. Check back later

If you want to develop for the CC1110 on the EdisonExplorer board, start by installing the spi_serial library.

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

Once you've cloned and made that program, you can flash a new hex file to the CC1110 using the following command:

ccprog -p 19,7,36 write path/to/firmware.hex

Note: the 19,7,36 numbers in the above string refer to the Edison hardware
pins that are used to communicate with the CC1110. If you aren't using the
Explorer board, you may need to use different pin numbers.
