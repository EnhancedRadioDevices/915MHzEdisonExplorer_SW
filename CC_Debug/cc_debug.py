
from time import sleep
import mraa as m


# Debug commands
CMD_CHIP_ERASE = 0x10
CMD_WR_CONFIG = 0x19
CMD_RD_CONFIG = 0x24
CMD_READ_STATUS = 0x30
CMD_RESUME = 0x4C
CMD_DEBUG_INSTR_1B = (0x54 | 1)
CMD_DEBUG_INSTR_2B = (0x54 | 2)
CMD_DEBUG_INSTR_3B = (0x54 | 3)
CMD_BURST_WRITE = 0x80
CMD_GET_CHIP_ID = 0x68

# Debug status bitmasks
STATUS_CHIP_ERASE_BUSY_BM = 0x80    # New debug interface
STATUS_PCON_IDLE_BM = 0x40
STATUS_CPU_HALTED_BM = 0x20
STATUS_PM_ACTIVE_BM = 0x10
STATUS_HALT_STATUS_BM = 0x08
STATUS_DEBUG_LOCKED_BM = 0x04
STATUS_OSC_STABLE_BM = 0x02
STATUS_STACK_OVERFLOW_BM = 0x01

# Start addresses on DUP (Increased buffer size improves performance)
ADDR_BUF0 = 0xf000        # Buffer (512 bytes)
FLASH_BUF_LEN = 0x0200    # Buffer length (512)
ADDR_DMA_DESC = 0xff00    # DMA descripotr (8 bytes)

# DMA channels used on DUP
CH_DBG_TO_BUF0 = 0x01    # Channel 0
CH_BUF0_TO_FLASH = 0x02  # Channel 1

# DUP registers (XDATA space address)
DUP_FCTL = 0xDFAE         # Flash controller
DUP_FADDRL = 0xDFAC       # Flash controller addr
DUP_FADDRH = 0xDFAD      # Flash controller addr
DUP_FWDATA = 0xDFAF      # Clash controller data buffer
DUP_DMA0CFGL = 0xDFD4     # Low byte, DMA config ch. 0
DUP_DMA0CFGH = 0xDFD5    # Low byte, DMA config ch. 0
DUP_DMAARM = 0xDFD6       # DMA arming register

# MRAA Edison Pin numbers
CC_DC = 19                # debug clock: P2_2 on CC1110, GP19 on Edison
CC_DD = 7                 # debug data: P2_1 on CC1110, GP20 on Edison
CC_RST = 36               # rst, GP14 on Edison

gpioDC = m.Gpio(CC_DC)
gpioDD = m.Gpio(CC_DD)
gpioRST = m.Gpio(CC_RST)


# Utility macros
# Set programmer DD line as input
def SET_DD_INPUT():
    gpioDD.dir(m.DIR_IN)


# Set programmer DD line as output
def SET_DD_OUTPUT():
    gpioDD.dir(m.DIR_OUT)


# Low nibble of 16bit variable
def LOBYTE(w):
    return (w & 0xFF)


# High nibble of 16bit variable
def HIBYTE(w):
    return ((w >> 8) & 0xFF)

# DUP DMA descriptor
dma_desc = [
  # Buffer -> Flash controller
  HIBYTE(ADDR_BUF0),              # src[15:8]
  LOBYTE(ADDR_BUF0),              # src[7:0]
  HIBYTE(DUP_FWDATA),             # dest[15:8]
  LOBYTE(DUP_FWDATA),             # dest[7:0]
  HIBYTE(FLASH_BUF_LEN),          # len[12:8]
  LOBYTE(FLASH_BUF_LEN),          # len[7:0]
  0x12,                           # trigger: Flash data write complete
  0x42,                           # increment source, DMA high priority
]


###########################################################################
# @brief    Writes a byte on the debug interface. Requires DD to be
#           output when function is called.
#
# @param    data    Byte to write
#
# @return   None.
###########################################################################
def write_debug_byte(data):
    for i in range(8):
        # Set clock high and put data on DD line
        gpioDC.write(1)
        gpioDD.write(data & 0x80)
        data <<= 1
        gpioDC.write(0)


###########################################################################
# @brief    Reads a byte from the debug interface. Requires DD to be
#           input when function is called.
#
# @return   Returns the byte read.
###########################################################################
def read_debug_byte():
    data = 0
    for i in range(8):
        gpioDC.write(1)
        data <<= 1
        data |= gpioDD.read()  # Read DD line
        gpioDC.write(0)
    return data


##########################################################################
# @brief    Function waits for DUP to indicate that it is ready. The DUP
#           will pulls DD line low when it is ready. Requires DD to
#           be input when function is called.
#
# @return   Returns 0 if function timed out waiting for DD line to go
#           low
# @return   Returns 1 when DUP has indicated it is ready.
###########################################################################
def wait_dup_ready():
    # DUP pulls DD low when ready
    count = 0
    while (gpioDD.read() and count < 16):
        # Clock out 8 bits before checking if DD is low again
        read_debug_byte()
        count += 1

    return False if (count == 16) else True


###########################################################################
# @brief    Issues a command on the debug interface. Only commands that
#           return one output byte are supported.
#
# @param    cmd             Command byte
# @param    cmd_bytes       Pointer to the array of data bytes following
#                           the command byte [0-3]
# @return   Data returned by command
###########################################################################
def debug_command(cmd, cmd_bytes):
    output = 0

    # Make sure DD is output
    SET_DD_OUTPUT()

    # Send command
    write_debug_byte(cmd)

    # Send bytes
    for i in range(len(cmd_bytes)):
        write_debug_byte(cmd_bytes[i])

    # Set DD as input
    SET_DD_INPUT()

    # Wait for data to be ready
    wait_dup_ready()

    # Read returned byte
    output = read_debug_byte()

    # Set DD as output
    SET_DD_OUTPUT()

    return output


###########################################################################
# @brief    Resets the DUP into debug mode. Function assumes that
#           the programmer I/O has already been configured using e.g.
#           programmer_init().
#
# @return   None.
###########################################################################
def debug_init():
    # Send two flanks on DC while keeping RESET_N low
    # All low (incl. RESET_N)
    gpioRST.write(0)
    gpioDC.write(0)
    gpioDD.write(0)
    cc_delay(1)       # Wait
    gpioDC.write(1)   # DC high
    gpioDC.write(0)   # DC low
    gpioDC.write(1)   # DC high
    gpioDC.write(0)   # DC low
    cc_delay(1)       # Wait
    gpioRST.write(1)
    print("letting go of reset")
    cc_delay(1)

    # Not sure why this is necessary, but the cc-debugger does it
    ok = debug_command(CMD_DEBUG_INSTR_1B, [0])
    cc_delay(1)

    ok = debug_command(CMD_READ_STATUS, [0])
    print("status = " + str(ok))

    cc_delay(1)

    ok = read_xdata_memory(0xDFC6)
    print("CLKCON = 0x%02x\n", str(ok))

    # Write FWT for 24MHz clock (24MHz = 0x20)
    ok = write_xdata_memory(0xDFAB, 0x20)
    print("Updated FWT: " + str(ok))
    cc_delay(1)

    # Read FWT
    ok = read_xdata_memory(0xDFAB)
    print("FWT = " + str(ok))
    cc_delay(1)

    # Write Config
    ok = debug_command(CMD_WR_CONFIG, [0x22])
    print("Debug Config = 0x%02x\n", ok)
    cc_delay(1)

    # Read Config
    ok = debug_command(CMD_RD_CONFIG, [])
    print("Wrote debug config: " + str(ok))


###########################################################################
# @brief    Reads the chip ID over the debug interface using the
#           GET_CHIP_ID command.
#
# @return   Returns the chip id returned by the DUP
###########################################################################
def read_chip_id():
    # Make sure DD is output
    SET_DD_OUTPUT()

    # Send command
    write_debug_byte(CMD_GET_CHIP_ID)

    # Set DD as input
    SET_DD_INPUT()

    # Wait for data to be ready
    wait_dup_ready()

    # Read ID and revision
    id = read_debug_byte()  # ID
    read_debug_byte()       # Revision (discard)

    # Set DD as output
    SET_DD_OUTPUT()

    return id


###########################################################################
# @brief    Sends a block of data over the debug interface using the
#           BURST_WRITE command.
#
# @param    src         Pointer to the array of input bytes
#
# @return   None.
###########################################################################
def burst_write_block(src):
    # Make sure DD is output
    SET_DD_OUTPUT()

    write_debug_byte(CMD_BURST_WRITE | HIBYTE(len(src)))
    write_debug_byte(LOBYTE(len(src)))
    for i in range(len(src)):
        write_debug_byte(src[i])

    # Set DD as input
    SET_DD_INPUT()

    # Wait for DUP to be ready
    wait_dup_ready()

    # ignore output
    read_debug_byte()

    # Set DD as output
    SET_DD_OUTPUT()


###########################################################################
# @brief    Issues a CHIP_ERASE command on the debug interface and
#           waits for it to complete.
#
# @return   None.
###########################################################################
def chip_erase():
    # Send command
    debug_command(CMD_CHIP_ERASE, [0])

    # Wait for status bit 7 to go low
    status = debug_command(CMD_READ_STATUS, [0])
    while((status & STATUS_CHIP_ERASE_BUSY_BM)):
        status = debug_command(CMD_READ_STATUS, [0])


###########################################################################
# @brief    Writes a block of data to the DUP's XDATA space.
#
# @param    address     XDATA start address
# @param    values      Pointer to the array of bytes to write
#
# @return   None.
###########################################################################
def write_xdata_memory_block(address, values):
    debug_command(CMD_DEBUG_INSTR_1B, [0])

    # MOV DPTR, address
    instr = [0x90, HIBYTE(address), LOBYTE(address)]
    print(instr, len(values))
    debug_command(CMD_DEBUG_INSTR_3B, instr)

    for i in range(len(values)):
        # MOV A, values[i]
        instr = [0x74, values[i]]
        debug_command(CMD_DEBUG_INSTR_2B, instr)

        # MOV @DPTR, A
        instr = [0xF0]
        debug_command(CMD_DEBUG_INSTR_1B, instr)

        # INC DPTR
        instr = [0xA3]
        debug_command(CMD_DEBUG_INSTR_1B, instr)


###########################################################################
# @brief    Writes a byte to a specific address in the DUP's XDATA
#           space.
#
# @param    address     XDATA address
# @param    value       Value to write
#
# @return   None.
###########################################################################
def write_xdata_memory(address, value):
    debug_command(CMD_DEBUG_INSTR_1B, [0])

    # MOV DPTR, address
    instr = [0x90, HIBYTE(address), LOBYTE(address)]
    debug_command(CMD_DEBUG_INSTR_3B, instr)

    # MOV A, values[i]
    instr = [0x74, value]
    debug_command(CMD_DEBUG_INSTR_2B, instr)

    # MOV @DPTR, A
    instr = [0xF0]
    debug_command(CMD_DEBUG_INSTR_1B, instr)


###########################################################################
# @brief    Read a byte from a specific address in the DUP's XDATA
#           space.
#
# @param    address     XDATA address
#
# @return   Value read from XDATA
###########################################################################
def read_xdata_memory(address):
    instr = []

    # MOV DPTR, address
    instr.append(0x90)
    instr.append(HIBYTE(address))
    instr.append(LOBYTE(address))
    debug_command(CMD_DEBUG_INSTR_3B, instr)

    # MOVX A, @DPTR
    instr = [0xE0]
    return debug_command(CMD_DEBUG_INSTR_1B, instr)


###########################################################################
# @brief    Reads 1-32767 bytes from DUP's flash to a given buffer on
#           the programmer.
#
# @param    address     Flash memory start address [0x0000 - 0x7FFF]
# @param    num_values  Number of data values to read.
#
# @return   values.
###########################################################################
def read_flash_memory_block(flash_addr, num_values):
    debug_command(CMD_DEBUG_INSTR_1B, [0])

    instr = []

    # 2. Move data pointer to XDATA address (MOV DPTR, xdata_addr)
    instr.append(0x90)
    instr.append(HIBYTE(flash_addr))
    instr.append(LOBYTE(flash_addr))
    debug_command(CMD_DEBUG_INSTR_3B, instr)

    values = []
    for i in range(num_values):
        # 3. Move value pointed to by DPTR to accumulator
        # (MOVX A, @DPTR)
        instr = [0xE0]
        values.append(debug_command(CMD_DEBUG_INSTR_1B, instr))

        # 4. Increment data pointer (INC DPTR)
        instr = [0xA3]
        debug_command(CMD_DEBUG_INSTR_1B, instr)
    return values


###########################################################################
# @brief    Writes bytes to DUP's flash memory.
#
# @param    src         Pointer to programmer's source buffer
#                      (in XDATA space)
# @param    start_addr  FLASH memory start address [0x0000 - 0x7FFF]
#
# @return   None.
###########################################################################
def write_flash_memory_block(src, start_addr):
    while len(src) < 4:
        src.append(0)

    start_byte = 0
    while start_byte < len(src):
        if len(src) - start_byte > 512:
            to_send = src[start_byte:start_byte+512]
        else:
            to_send = src[start_byte:]

        dma_desc[4] = HIBYTE(len(to_send))    # len[12:8]
        dma_desc[5] = LOBYTE(len(to_send))    # len[7:0]

        # 1. Write the DMA descriptor to RAM
        write_xdata_memory_block(ADDR_DMA_DESC, dma_desc)

        # 2. Set DMA controller pointer to the DMA descriptors
        write_xdata_memory(DUP_DMA0CFGH, HIBYTE(ADDR_DMA_DESC))
        write_xdata_memory(DUP_DMA0CFGL, LOBYTE(ADDR_DMA_DESC))

        # 3. Set Flash controller start address (wants 16MSb of 18 bit address)
        write_xdata_memory(DUP_FADDRH, HIBYTE((start_addr + start_byte) >> 1))
        write_xdata_memory(DUP_FADDRL, LOBYTE((start_addr + start_byte) >> 1))
        start_byte += len(to_send)

        # 4. Write data to buffer
        write_xdata_memory_block(ADDR_BUF0, to_send)

        # 5. Arm buffer -> flash DMA channel (channel 0)
        write_xdata_memory(DUP_DMAARM, 0x01)
        write_xdata_memory(DUP_FCTL, 0x02)    # Trigger write

        # 7. Wait until flash controller is done
        while (read_xdata_memory(DUP_FCTL) & 0x80):   # Should this be DUP_?
            pass


def cc_delay(micros):
    sleep(micros/1000000.0)


def setup():
    gpioDC.dir(m.DIR_OUT)
    gpioDD.dir(m.DIR_OUT)
    gpioRST.dir(m.DIR_OUT)
    gpioDD.write(1)

TOTAL_FLASH_SIZE = 0x830
FLASH_BLOCK_SIZE = 0x400


def dump_flash(fname):
    f = open(fname, 'w')
    print("Reading flash.")
    flash_buf = read_flash_memory_block(0x0000, TOTAL_FLASH_SIZE)
    f.write(flash_buf)
    f.close()

if __name__ == "__main__":
    import argparse
    import sys

    # possible options:
    # - get the device ID (-i)
    # - reset device (-r)
    # - erase device (-e)
    # - program a given file to the device (--p filename)
    # - read the file currently on the device (--s new_filename)
    parser = argparse.ArgumentParser(description='CC Debugger')
    parser.add_argument('--r', action='store_true',
                        help='temporarily reset the device')
    parser.add_argument('--i', action='store_true',
                        help='get the device ID')
    parser.add_argument('--e', action='store_true',
                        help='erase the device')
    parser.add_argument('--p', dest='source_file', default=None,
                        help='program a hex file to the device')
    parser.add_argument('--s', dest='dest_file', default=None,
                        help='read a hex file from the device')

    args = parser.parse_args()

    setup()
    debug_init()

    if args.r:
        gpioRST.write(0)
        cc_delay(10)
        gpioRST.write(1)

    if args.e:
        chip_erase()
        print("chip erased")

    if args.i:
        print("chip id: " + str(read_chip_id()))

    if args.source_file is not None:
        print("* Opening hex file")
        try:
            src_hex = open(args.source_file, 'r')
        except:
            print("Error opening source file " + str(args.source_file))
            sys.exit(1)   # Error
        print("* Erasing Chip")
        chip_erase()
        print("* Chip erased")
        line_num = 0
        for line in src_hex:
            line_num += 1
            line = line.strip()
            # hex files are of format :llaaaatt[dd...]cc
            if line[0] != ':':
                print("Error: illegal hex file line " + str(line_num))
                sys.exit(1)
            num_data_bytes = int(line[1:3], 16)
            addr = int(line[3:7], 16)
            data_type = int(line[7:9], 16)
            data = line[9:-2]
            checksum = line[-2:]
            # TODO: read checksum
            if data_type == 1:
                # end of file
                sys.exit(0)
            elif data_type == 0:
                # data
                # w_f_m_b expects at least four bytes
                # what todo about that?
                encoded_data = [ord(x) for x in data.decode('hex')]
                write_flash_memory_block(encoded_data, addr)
            else:
                print("Erro: unimplemented data type")
                sys.exit(1)
        src_hex.close()

    if args.dest_file is not None:
        print("* Opening hex file")
        try:
            dest_hex = open(args.dest_file, 'w')
        except:
            print("Error opening destination file " + str(args.dest_file))
            sys.exit(1)   # Error
            addr_step = 64
            addr = 0
        while addr < (8*32738):   # Max of 8 banks to read
            hex = read_flash_memory_block(
              addr / 32768,
              addr % 32768,
              addr_step
            )
            addr += addr_step
            # TODO: print hex to file with specified format
            # (currently just spitting out bytes)
            line = ":"
            line += '{:02x}'.format(len(data)).zfill(2)
            line += '{:02x}'.format(addr).zfill(4)
            line += '00'
            line += ''.join('{:02x}'.format(x) for x in hex)
            encoded_data = [ord(x) for x in line[1:].decode('hex')]
            line += '{:02x}'.format(sum(encoded_data))
            dest_hex.write(line)
        dest_hex.write(':00000001FF')
        dest_hex.close()
