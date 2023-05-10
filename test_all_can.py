#!/usr/bin/env python3
import time
import can
import canopen
from argparse import ArgumentParser

parser = ArgumentParser(description = 'canio arguments')
parser.add_argument("can_interface", help = "can0 or can1 ...", type = str)
parser.add_argument("can_bitrate", help = "can bitrate", type = str)
parser.add_argument("can_id", help = "can id of the device", type = str)
parser.add_argument("node_id", help = "lss node ID", type = str)

class all_can_canopen():
    
    can_interface = parser.parse_args().can_interface
    bitra = int(parser.parse_args().can_bitrate)
    can_id = parser.parse_args().can_id
    node_id = int(parser.parse_args().node_id)
    
    def __init__(self) -> None:
        self.network = canopen.Network()
        self.network.connect(bustype='socketcan', channel=self.can_interface, bitrate=self.bitra)
        self.node = self.network.add_node(int(self.can_id), 'objdict.eds')

    def entry_operable(self):
        self.network.nmt.state = 'OPERATIONAL'
    
    def set_heartbeat(self, value) -> None:
        val = value.to_bytes(4, byteorder='little')
        self.node.sdo.download(0x1017, 0, val)
            
    def monitor_heartbeat(self):
        try:
            self.node.nmt.wait_for_heartbeat()
            print("CAN Heartbeat Received")
            return False
        except canopen.nmt.HeartbeatError:
            print("CAN Heartbeat Error")
            return True

    def monitor_error(self):
        try:
            error = self.node.emcy.wait(timeout=1)
            if error is not None:
                print(f"Error Code: {error.code:#x}, Error Register: {error.reg:#x}")
                return True
        except canopen.emcy.EmcyError:
            print("No Error Frame Received")
            return False

    def reset_node(self):
        try:
            self.node.nmt.state = 'RESET'
            print("CAN Error, RESET")
        except Exception as e:
            print(e)
    
    def PowerErrorReport(self):
        power_state = {
                '0': 'no error',
                '1': 'vcc 24V error',
                '2': 'vcc 5v error',
                '4': 'vcc 3.3v error',
                '8': '2.5v error'
            }
        try:
            val = self.node.sdo[0x2001]
            print("Power Error Report: ", power_state[str(val.raw)])
        except Exception as e:
            print(e)

    def sensorModeSwitch(self) -> None:
        module_state = {
            '0': 'self-inspection',
            '1': 'initialize',
            '2': 'working',
            '3': 'error',
            '4': 'upgrade'
        }
        try:
            val = self.node.sdo[0x2002]
            print("sensor Mode Switch: ", module_state[str(val.raw)])
        except Exception as e:
            print(e)
            
    def workModeSwitch(self, operate, value=1) -> None:
        """work Mode Switch

        Args:
            operate (str):  'r' or 'w'.
            value (int, optional): 1 2 3 -> Mode A B C. Defaults to 1.
        """
        module_state = {
            '1': 'Mode A',
            '2': 'Mode B',
            '3': 'Mode C'
        }
        try:
            if operate == 'r':
                val = self.node.sdo[0x2003]
                print("read work Mode Switch: ", module_state[str(val.raw)])
            elif operate == "w":
                val = value.to_bytes(1, byteorder='little')
                self.node.sdo.download(0x2003, 0, val)
        except Exception as e:
            print(e)

    def gpioRead(self) -> None:
        gpio_state = {
            '0': 'no IO',
            '1': 'DIO1',
            '2': 'DIO2',
            '4': 'DIO3',
            '8': 'DIO4',
            '16': 'DIO5'
        }
        try:
            val = self.node.sdo[0x2004]
            print("sensor Mode Switch: ", gpio_state[str(val.raw)])
        except Exception as e:
            print(e)

    def event_timer(self, operate: str, value=0) -> None:
        """event timer

        Args:
            operate (str): 'r' or 'w'.
            value (int, optional): gpio Read report timer (ms). Defaults to 0.
        """
        try:
            if operate == 'r':
                val = self.node.sdo[0x1800][5]
                print("read event timer: ", val.raw)
            elif operate == 'w':
                val = value.to_bytes(2, byteorder='little')
                self.node.sdo.download(0x1800, 5, val)
                print(f"set event timer: {value}ms")
        except Exception as e:
            print(e)

    def gpioPower(self, operate: str, value=0) -> None:
        """gpio Power

        Args:
            operate (str): 'r' or 'w'.
            value (int, optional): 0 close 1 open. Defaults to 0.
        """
        try:
            if operate == 'r':
                val = self.node.sdo[0x2005]
                print("GPIO Power Mode: ", val.raw)
            elif operate == 'w':
                val = value.to_bytes(1, byteorder='little')
                self.node.sdo.download(0x2005, 0, val)
                print(f"GPIO Power Mode: {value}")
        except Exception as e:
            print(e)

    def encoderValueRead(self) -> None:
        try:
            val = self.node.sdo[0x2006]
            print(f'encoder Value Read: {val.raw}')
        except Exception as e:
            print(e)

    def encoderPower(self, operate: str, value=0) -> None:
        """encoder Power

        Args:
            operate (str): 'r' or 'w'.
            value (int, optional): 0 close 1 open. Defaults to 0.
        """
        try:
            if operate == 'r':
                val = self.node.sdo[0x2007]
                print("read encoder Power Mode: ", val.raw)
            elif operate == 'w':
                val = value.to_bytes(1, byteorder='little')
                self.node.sdo.download(0x2007, 0, val)
                print(f"write encoder Power Mode: {value}")
        except Exception as e:
            print(e)

    def encoder_read_val(self, operate: str, value=0) -> None:
        """设置编码器值的上报时间

        Args:
            operate (str): 'r' or 'w'.
            value (int, optional): gpio Read report timer (ms). Defaults to 0.
        """
        try:
            if operate == 'r':
                val = self.node.sdo[0x1801][5]
                print("read encoder val: ", val.raw)
            elif operate == 'w':
                val = value.to_bytes(2, byteorder='little')
                self.node.sdo.download(0x1801, 5, val)
                print(f"set encoder timer: {value}ms")
        except Exception as e:
            print(e)

    def config_node_id(self) -> None:
        try:
            vendor_id = self.node.sdo[0x1018][1].raw
            print("Vendor-ID: ", vendor_id)
            product_code = self.node.sdo[0x1018][2].raw
            print("Product Code: ", product_code)
            revision_version = self.node.sdo[0x1018][3].raw
            print("Revision Version: ", revision_version)
            serial_number = self.node.sdo[0x1018][4].raw
            print("Serial Number: ", serial_number)
        
            ret_bool = self.network.lss.send_switch_state_selective(vendor_id, product_code, revision_version, serial_number)

            if ret_bool:
                node_id = self.network.lss.inquire_node_id()
                print("node_id:", node_id)

                self.network.lss.configure_node_id(3)
                time.sleep(0.5)
                self.network.lss.store_configuration()
                time.sleep(0.5)
                self.network.lss.send_switch_state_global(self.network.lss.WAITING_STATE)
                time.sleep(0.5)

        except Exception as e:
            print(e)

    def __delattr__(self, __name: str) -> None:
        self.network.sync.stop()
        self.network.disconnect()

if __name__ == "__main__":
    test1 = all_can_canopen()

    test1.entry_operable()
    test1.workModeSwitch('w', 1)
    test1.workModeSwitch('r', 1)
    test1.gpioPower('w', 1)

