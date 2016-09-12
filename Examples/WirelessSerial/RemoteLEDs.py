
import spi_serial
import struct
import time

def send_get_pkt_cmd(ss, chan, timeout):
    timeout = struct.pack("<I", int(timeout))
    cmd = [3, chan]
    cmd.extend(timeout)
    ss.write(cmd)

if __name__ == "__main__":
    import argparse
    
    # possible options:
    # - select channel (--c)
    parser = argparse.ArgumentParser(description='RemoteLEDs Explorer Control')
    parser.add_argument('--c', dest='channel', default=0,
                    help='set rx channel')

    args = parser.parse_args()

	
	ss = spi_serial.SpiSerial()

    cmd = [1]
    ss.write(cmd)
    resp = ss.read(0)
    if resp != [79, 75, 0]:
        print "couldn't find CC1110"
        return

    while True:
        try:
            send_get_cmd_pkt(ss, args.channel, 2222)
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
