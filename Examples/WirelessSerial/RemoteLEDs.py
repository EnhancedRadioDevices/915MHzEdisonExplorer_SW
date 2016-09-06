
import spi_serial
import struct
import time

def freq_to_chan(freq):
    return 66

def send_get_pkt_cmd(ss, freq, timeout):
    timeout = struct.pack("<I", int(timeout))
    cmd = [3, freq_to_chan(freq)]
    cmd.extend(timeout)
    ss.write(cmd)

if __name__ == "__main__":
    ss = spi_serial.SpiSerial()

    cmd = [1]
    ss.write(cmd)
    resp = ss.read(0)
    if resp != [79, 75, 0]:
        print "couldn't find CC1110"
        return

    while True:
        try:
            send_get_cmd_pkt(ss, 908, 2222)
            while ss.inWaiting() == 0:
                time.sleep(1)
            resp = ss.read(0)
            print(resp)
            if len(resp) > 2:
                # we got a packet
                if len(resp) == 5 and resp[2] == 8:
                    # LED cntl packet
                    ss.write(resp[2:5])
        except:
            break
