
# 915MHz Serial Link

The python script in this directory allows for simple tranmission of commands and data to the CC1110. The CC1110 can parse these commands and then transmit and receive data with other Explorer boards as needed.

# BLE to Serial Link

This example serves as a BLE to 915 serial bridge. Running the node.js script will start a BLE peripheral with one characteristic. Writing to that characteristic (from e.g. a Smartphone) will cause the string you write to be transmitted to the CC1110 on the Explorer board and interpreted as a serial command.


