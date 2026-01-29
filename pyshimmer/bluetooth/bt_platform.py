# pyshimmer - Python API for Shimmer sensor devices
# Copyright (C) 2020  Lukas Magel

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import os
import sys
from typing import Iterable, List, Optional

from pyshimmer.ports import SerialPort, filter_serial_ports, list_serial_ports, resolve_serial_port


def _platform_name() -> str:
    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    return "linux"


def bluetooth_setup_hint() -> str:
    platform = _platform_name()
    if platform == "windows":
        return (
            "Pair the Shimmer in Windows Bluetooth settings and use the COM port "
            "exposed for the device (Device Manager -> Ports)."
        )
    if platform == "macos":
        return (
            "Pair the Shimmer in System Settings -> Bluetooth and use the /dev/cu.* "
            "device that appears for it."
        )
    return (
        "Pair the device and create an rfcomm port (e.g. rfcomm bind) so it "
        "appears as /dev/rfcommN."
    )


def _format_ports(ports: Iterable[SerialPort]) -> str:
    lines = []
    for port in ports:
        desc = port.description or "unknown"
        mfg = port.manufacturer or "unknown"
        lines.append(f"- {port.device} ({desc}, {mfg})")
    return "\n".join(lines)


def suggest_bluetooth_ports() -> List[SerialPort]:
    platform = _platform_name()
    if platform == "linux":
        ports = filter_serial_ports(match="rfcomm")
        if ports:
            return ports
        return filter_serial_ports(match="bluetooth")
    if platform == "macos":
        ports = filter_serial_ports(match="bluetooth")
        if ports:
            return ports
        return filter_serial_ports(match="/dev/cu.")
    ports = filter_serial_ports(match="bluetooth")
    if ports:
        return ports
    return []


def resolve_bluetooth_port(
    port: Optional[str] = None,
    env_var: str = "PYSHIMMER_BT_PORT",
) -> str:
    if port is None:
        port = os.environ.get(env_var)
    if port is not None:
        return resolve_serial_port(port=port)

    candidates = suggest_bluetooth_ports()
    if len(candidates) == 1:
        return resolve_serial_port(port=candidates[0].device)

    available = list_serial_ports()
    available_str = _format_ports(available) if available else "- (no ports found)"
    if not candidates:
        raise ValueError(
            "No Bluetooth serial ports found. "
            + bluetooth_setup_hint()
            + "\nAvailable ports:\n"
            + available_str
        )
    raise ValueError(
        "Multiple Bluetooth serial ports found. Please disambiguate by providing a "
        "specific port via function argument or "
        f"{env_var}.\nAvailable ports:\n"
        + available_str
    )
