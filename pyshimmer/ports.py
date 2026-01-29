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
from dataclasses import dataclass
from typing import Iterable, List, Optional

from serial.tools import list_ports


@dataclass(frozen=True)
class SerialPort:
    device: str
    description: Optional[str]
    hwid: Optional[str]
    manufacturer: Optional[str]
    product: Optional[str]
    serial_number: Optional[str]
    vid: Optional[int]
    pid: Optional[int]
    location: Optional[str]
    interface: Optional[str]


def list_serial_ports() -> List[SerialPort]:
    ports: List[SerialPort] = []
    for info in list_ports.comports():
        ports.append(
            SerialPort(
                device=info.device,
                description=info.description,
                hwid=info.hwid,
                manufacturer=getattr(info, "manufacturer", None),
                product=getattr(info, "product", None),
                serial_number=getattr(info, "serial_number", None),
                vid=getattr(info, "vid", None),
                pid=getattr(info, "pid", None),
                location=getattr(info, "location", None),
                interface=getattr(info, "interface", None),
            )
        )
    return ports


def _matches_text(port: SerialPort, match: str) -> bool:
    match_l = match.lower()
    fields = (
        port.device,
        port.description,
        port.hwid,
        port.manufacturer,
        port.product,
        port.serial_number,
    )
    for field in fields:
        if field and match_l in field.lower():
            return True
    return False


def _matches_vid_pid(port: SerialPort, vid: Optional[int], pid: Optional[int]) -> bool:
    if vid is not None and port.vid != vid:
        return False
    if pid is not None and port.pid != pid:
        return False
    return True


def filter_serial_ports(
    match: Optional[str] = None,
    vid: Optional[int] = None,
    pid: Optional[int] = None,
) -> List[SerialPort]:
    ports = list_serial_ports()
    result: List[SerialPort] = []
    for port in ports:
        if match and not _matches_text(port, match):
            continue
        if not _matches_vid_pid(port, vid, pid):
            continue
        result.append(port)
    return result


def _format_ports(ports: Iterable[SerialPort]) -> str:
    lines = []
    for port in ports:
        desc = port.description or "unknown"
        mfg = port.manufacturer or "unknown"
        lines.append(f"- {port.device} ({desc}, {mfg})")
    return "\n".join(lines)


def _normalize_port(port: str) -> str:
    if sys.platform.startswith("win"):
        port_upper = port.upper()
        if port_upper.startswith("COM") and len(port_upper) > 4:
            return f"\\\\.\\{port_upper}"
    return port


def resolve_serial_port(
    port: Optional[str] = None,
    match: Optional[str] = None,
    vid: Optional[int] = None,
    pid: Optional[int] = None,
    env_var: str = "PYSHIMMER_PORT",
) -> str:
    if port is None:
        port = os.environ.get(env_var)
    if port is not None:
        return _normalize_port(port)

    if match is None and vid is None and pid is None:
        raise ValueError(
            "No serial port specified. Provide a port string, set "
            f"{env_var}, or pass match/vid/pid to resolve_serial_port()."
        )

    ports = filter_serial_ports(match=match, vid=vid, pid=pid)
    if len(ports) == 1:
        return _normalize_port(ports[0].device)

    available = list_serial_ports()
    available_str = _format_ports(available) if available else "- (no ports found)"
    if not ports:
        raise ValueError(
            "No matching serial ports found. Available ports:\n"
            + available_str
        )
    raise ValueError(
        "Multiple serial ports matched. Please disambiguate by providing a "
        "specific port. Available ports:\n" + available_str
    )
