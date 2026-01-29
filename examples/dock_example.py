from serial import Serial

from pyshimmer import ShimmerDock, DEFAULT_BAUDRATE, fmt_hex, resolve_serial_port


def main(args=None):
        # Set PYSHIMMER_PORT to your dock serial port, e.g. /dev/ttyUSB0, /dev/cu.* or COM4
        port = resolve_serial_port()
        serial = Serial(port, DEFAULT_BAUDRATE)

        print(f'Connecting docker')
        shim_dock = ShimmerDock(serial)

        mac = shim_dock.get_mac_address()
        print(f'Device MAC: {fmt_hex(mac)}')

        shim_dock.close()


if __name__ == '__main__':
    main()        
