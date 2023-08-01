import sys
from time import sleep
from typing import Any

from rich import print

from metaprocessor.helpers.decorator import metawear

if sys.platform == "linux":
    from mbientlab.metawear import (
        MetaWear,  # https://github.com/mbientlab/metawear-sdk-python
    )
    from mbientlab.warble import (
        BleScanner,  # https://github.com/mbientlab/pywarble
    )


@metawear
def scan(timeout: float) -> str:
    selection = -1
    devices = {}

    while selection == -1:
        print("Scanning for devices...")

        def handler(result: Any) -> None:
            devices[result.mac] = result.name

        BleScanner.set_handler(handler)
        BleScanner.start()
        sleep(timeout)
        BleScanner.stop()

        for index, address, name in enumerate(devices.items()):
            print(f"{index} {address} {name}")

        selection = int(input("Select your device (-1 to re-scan): "))

    return list(devices)[selection]


@metawear
def connect(mac: str) -> Any:
    device = MetaWear(mac)
    device.connect()
    print(f"Connected to {device.address} via {'serial connection' if device.usb.is_connected else 'Bluetooth Low Energy'}")
    return device


@metawear
def disconnect(device: Any) -> None:
    device.disconnect()
    print(f"Disconnected from {device.address}")
