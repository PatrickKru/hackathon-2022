import asyncio
import time
from typing import Awaitable

from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice

KNOWN_DEVICES_FILE = "knownDevices.txt"

PERIOD = 4.0
# TIMEOUT = PERIOD + 1 # timeout > period
# TIMEOUT = PERIOD + 4  # timeout > period
TIMEOUT = 3  # timeout > period
AVAILABILITY_SLOT = 0.5

address = "24:0A:C4:EE:50:BA"
# address = "24:0A:F4:ED:50:BA"

characteristic_uuid = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
period_uuid = ""
message_size_uuid = ""

rssi = 0

def print_device(device: BLEDevice):
    print("address:", device.address)
    print("name:", device.name)
    print("details:", device.details)
    print("rssi:", device.rssi)
    print("metadata:", device.metadata)


async def find_device(device_address: str):
    return await BleakScanner.find_device_by_address(device_address, timeout=TIMEOUT)


async def discover():
    devices = await BleakScanner.discover()
    # device = filter(lambda d: (d.address == address), devices)
    # print_device(device)
    for d in devices:
        # print(type(d))
        #     print_device(d)
        print(d)


async def blue_read():
    async with BleakClient(address) as client:
        model_number = await client.read_gatt_char(characteristic_uuid)
        print("Model Number: {0}".format("".join(map(chr, model_number))))


async def blue_write(uuid: str, msg: str):
    async with BleakClient(address) as client:
        model_number = await client.write_gatt_char(uuid, bytes(msg, "ascii"))
        print("Model Number: {0}".format("".join(map(chr, model_number))))


async def blue_write_int(uuid: str, msg: int):
    async with BleakClient(address) as client:
        model_number = await client.write_gatt_char(uuid, bytes([msg]))
        print("Model Number: {0}".format("".join(map(chr, model_number))))


def handle_selection(selection: str):
    if selection == "p":
        period = int(input("period size:"))
        blue_write_int(period_uuid, period)
    elif selection == "m":
        message_length = int(input("message length:"))
        blue_write_int(message_size_uuid, message_length)
    else:
        print("Unsupported input")


def read_config():
    selection = input("Set period[p] or message length[m]:")

    try:
        handle_selection(selection)
    except ValueError:
        print("Whoops, the input is not a positive integer")


def get_available_device():
    with open(KNOWN_DEVICES_FILE, "r") as file:
        known_devices = file.readlines()
        for known_device in known_devices:
            device = asyncio.run(find_device(known_device))
            if device is not None:
                return device

    return None


def main():
    device = get_available_device()
    if device is None:
        print("No known device available")
        print(f"Add a known device to the {KNOWN_DEVICES_FILE} file")
        print("Available devices:")
        asyncio.run(discover())
        return

    asyncio.run(connect_to_device(device))


async def connect_to_device(device: BLEDevice):
    async with BleakClient(address) as client:
        print(f"Connected to device {device.name}")
        value = await client.read_gatt_char(characteristic_uuid)
        result = "".join(map(chr, value))
        print(f"Value: {result}, Rssi: {device.rssi}")


async def callback(BLEDevice, AdvertisementData) -> Awaitable[None]:
    print(BLEDevice)
    print(AdvertisementData)


# An easy notify function, just print the receive data
def notification_handler(sender, data):
    print(', '.join('{:02x}'.format(x) for x in data))


# class Handler:
#     def __init__(self):
#         self.notify_callback = None
#         self.notify_characteristic = None
#         self.on_disconnect = None
#         self.client = None
#         self.connection_enabled = None
#
#     async def connect_to_device(self):
#         while True:
#             if self.connection_enabled:
#                 try:
#                     await self.client.connect()
#                     self.connected = await self.client.is_connected()
#                     if self.connected:
#                         print("Connected to Device")
#                         self.client.set_disconnected_callback(self.on_disconnect)
#                         await self.client.start_notify(
#                             self.notify_characteristic, self.notify_callback,
#                         )
#                         while True:
#                             if not self.connected:
#                                 break
#                             await asyncio.sleep(1.0)
#                     else:
#                         print(f"Failed to connect to Device")
#                 except Exception as e:
#                     print(e)
#             else:
#                 await asyncio.sleep(1.0)
#

async def test():
    global rssi
    device = await BleakScanner.find_device_by_address(address, timeout=TIMEOUT)
    if device is not None:
        rssi = device.rssi

    async with BleakClient(address) as client:
        while client.is_connected:
            value = await client.read_gatt_char(characteristic_uuid)
            print(f"Value: {value}, Rssi: {rssi}")
        # await client.start_notify(
        #     characteristic_uuid, notification_handler,
        # )


async def test2():
    client = BleakClient(address)
    try:
        await client.connect()
        value = await client.read_gatt_char(characteristic_uuid)
        print(f"Value: {value}, Rssi: x")
    except Exception as e:
        print(e)
    finally:
        await client.disconnect()


def run():
    # loop = asyncio.get_event_loop()
    while True:
        try:
            asyncio.run(test())
        except:
            print("device disconnected")
            time.sleep(2)

    # try:
    #     asyncio.ensure_future(test())
    #     loop.run_forever()
    # except KeyboardInterrupt:
    #     print()
    #     print("User stopped program.")
    # finally:
    #     print("Disconnecting...")
    #     loop.close()


if __name__ == '__main__':
    # main()
    run()
    # asyncio.run(blue_write("hello"))
