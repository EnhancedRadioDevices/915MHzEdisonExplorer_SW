
import spi_serial

# TODO: create commands to control the CC1110

if __name__ == "__main__":
    ss = spi_serial.SpiSerial()

    #TODO: get stdin and handle it
    #TODO: push stdout
    while True:
        try:
            cmd = raw_input()
            ss.write([int(c) for c in cmd])
            if ss.inWaiting() > 0:
               print(ss.read(0))
        except:
            break
