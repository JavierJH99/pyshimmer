import argparse
import datetime
import time

from serial import Serial

from pyshimmer import (
    ShimmerBluetooth,
    DEFAULT_BAUDRATE,
    resolve_bluetooth_port,
)


def setup_shimmer(port: str, baudrate: int, init_sleep: float) -> ShimmerBluetooth:
    print(f"[info] opening port: {port}")
    serial = Serial(port, baudrate, timeout=2)
    time.sleep(init_sleep)

    shim = ShimmerBluetooth(serial)
    return shim


def main() -> None:
    parser = argparse.ArgumentParser(description="Bluetooth connection test with retries.")
    parser.add_argument("--port", type=str, default=None, help="Bluetooth serial port (e.g. /dev/cu.* or COM3)")
    parser.add_argument("--baudrate", type=int, default=DEFAULT_BAUDRATE, help="Serial baudrate")
    parser.add_argument("--init-sleep", type=float, default=5.0, help="Seconds to wait before initialize()")
    parser.add_argument("--retries", type=int, default=3, help="Number of initialize retries")
    parser.add_argument("--retry-delay", type=float, default=2.0, help="Seconds between retries")
    args = parser.parse_args()

    port = args.port or resolve_bluetooth_port()
    shim = setup_shimmer(port, args.baudrate, args.init_sleep)

    last_err = None
    for attempt in range(1, args.retries + 1):
        try:
            print(f"[info] initialize attempt {attempt}/{args.retries}")
            shim.initialize()
            print("[info] initialize OK")
            break
        except Exception as exc:
            last_err = exc
            print(f"[warn] initialize failed: {exc}")
            if attempt < args.retries:
                time.sleep(args.retry_delay)
    else:
        raise last_err

    now = datetime.datetime.now()
    unix_time = time.mktime(now.timetuple()) + now.microsecond / 1_000_000
    shim.set_config_time(unix_time)

    device_name = shim.get_device_name()
    fw_type, fw_ver = shim.get_firmware_version()
    sampling_rate = shim.get_sampling_rate()
    battery = shim.get_battery_state(True)

    print(f"[info] device: {device_name}")
    print(f"[info] firmware: {fw_type} {fw_ver.major}.{fw_ver.minor}.{fw_ver.rel}")
    print(f"[info] sampling rate: {sampling_rate} Hz")
    print(f"[info] battery: {battery:.0f}%")

    shim.shutdown()
    print("[info] done")


if __name__ == "__main__":
    main()
