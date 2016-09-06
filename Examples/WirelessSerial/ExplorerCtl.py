
import spi_serial

if __name__ == "__main__":
    ss = spi_serial.SpiSerial()

    while True:
        try:
            cmd = raw_input()
            cmd = [int(c) for c in cmd.split(',')]
            if cmd[0] != 0:
                ss.write(cmd)
            if ss.inWaiting() > 0:
               print(ss.read(0))
        except:
            break
