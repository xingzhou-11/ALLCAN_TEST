#!/usr/bin/env python3
import canopen
import time
# from argparse import ArgumentParser

# parser = ArgumentParser(description = 'canio arguments')
# parser.add_argument("can_interface", help = "can0 or can1 ...", type = str)
# parser.add_argument("can_bitrate", help = "can bitrate", type = str)
# parser.add_argument("now_node_id", help = "can id of the device", type = str)
# parser.add_argument("--new_node_id", help = "lss node ID", type = str, required=False)

class all_can_canopen():
    vendor_id = 0
    product_code = 0
    revision_version = 0
    serial_number = 0
    
    def __init__(self, can_interface, bitra, node_id) -> None:
        self.network = canopen.Network()
        self.network.connect(bustype='socketcan', channel=can_interface, bitrate=bitra)
        self.node = self.network.add_node(int(node_id), 'objdict.eds')

    def entry_operable(self):
        self.network.nmt.state = 'OPERATIONAL'
    
    def set_heartbeat(self, value) -> None:
        val = value.to_bytes(4, byteorder='little')
        self.node.sdo.download(0x1017, 0, val)
            
    def monitor_heartbeat(self):
        try:
            self.node.nmt.wait_for_heartbeat()
            print("CAN Heartbeat Received")
            return True
        except canopen.nmt.HeartbeatError:
            print("CAN Heartbeat Error")
            return False

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

    def stateModeSwitch(self) -> None:
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
                return val.raw
            elif operate == "w":
                val = value.to_bytes(1, byteorder='little')
                self.node.sdo.download(0x2003, 0, val)
        except Exception as e:
            print(f'error {e}')
            return False

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
            return val.raw
        except Exception as e:
            print(f'error {e}')
            return False

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
            print(f'error {e}')

    def gpioPower(self, operate: str, value=0) -> None:
        """gpio Power

        Args:
            operate (str): 'r' or 'w'.
            value (int, optional): 0 close 1 open. Defaults to 0.
        """
        try:
            if operate == 'r':
                val = self.node.sdo[0x2005].raw
                print("GPIO Power Mode: ", val)
                return val
            elif operate == 'w':
                val = value.to_bytes(1, byteorder='little')
                self.node.sdo.download(0x2005, 0, val)
                print(f"GPIO Power Mode: {value}")
                return value
        except Exception as e:
            print(f'error {e}')
            return False

    def encoderValueRead(self) -> None:
        """Read encoder Value            
        """
        try:
            val = self.node.sdo[0x2006].raw
            print(f'encoder Value Read: {val}')
            return val
        except Exception as e:
            print(f'error {e}')
            return False

    def encoderPower(self, operate: str, value=0) -> None:
        """encoder Power

        Args:
            operate (str): 'r' or 'w'.
            value (int, optional): 0 close 1 open. Defaults to 0.
        """
        try:
            if operate == 'r':
                val = self.node.sdo[0x2007].raw
                print("read encoder Power Mode: ", val)
                return val
            elif operate == 'w':
                val = value.to_bytes(1, byteorder='little')
                self.node.sdo.download(0x2007, 0, val)
                print(f"write encoder Power Mode: {value}")
                return value
        except Exception as e:
            print(f'error {e}')
            return False
    
    def encoder_read_time(self, operate: str, value=0) -> None:
        """设置编码器值的上报周期

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
            print(f'error {e}')

    def Power_5V(self, operate: str, value=0) -> None:
        """Power 5V

        Args:
            operate (str): 'r' or 'w'.
            value (int, optional): 0 close 1 open. Defaults to 0.
        """
        try:
            if operate == 'r':
                val = self.node.sdo[0x2009].raw
                print("GPIO Power Mode: ", val)
                return val
            elif operate == 'w':
                val = value.to_bytes(1, byteorder='little')
                self.node.sdo.download(0x2009, 0, val)
                print(f"GPIO Power Mode: {value}")
                return value
        except Exception as e:
            print(f'error {e}')
            return False

    def config_node_id(self, operate: str, new_node_id=1, vendor_id=0, product_code=0, revision_version=0, serial_number=0) -> None:
        try:
            if operate == 'r':
                vendor_id = self.node.sdo[0x1018][1]
                product_code = self.node.sdo[0x1018][2]
                revision_version = self.node.sdo[0x1018][3]
                serial_number = self.node.sdo[0x1018][4]

                print("Vendor-ID str: ", vendor_id.get_data().decode('utf-8')[::-1])
                print("Vendor-ID int: ", vendor_id.raw)
                print("Product Code int: ", product_code.raw)
                print("Revision Version int: ", revision_version.raw)
                print("Serial Number int: ", serial_number.raw)

            elif operate == 'w':
                ret_bool = self.network.lss.send_switch_state_selective(vendor_id, product_code, revision_version, serial_number)

                if ret_bool:
                    self.network.lss.configure_node_id(new_node_id)
                    self.network.lss.store_configuration()
                    self.network.lss.send_switch_state_global(self.network.lss.WAITING_STATE)

        except Exception as e:
            print(f'error: {e}')
            return False

    def __delattr__(self, __name: str) -> None:
        self.network.sync.stop()
        self.network.disconnect()