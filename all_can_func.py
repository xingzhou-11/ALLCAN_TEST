#!/usr/bin/env python3
import canopen
import sys

class all_can_canopen():
    vendor_id = 0
    product_code = 0
    revision_version = 0
    serial_number = 0
    
    def __init__(self, can_interface, bitra, node_id) -> None:
        self.network = canopen.Network()
        self.network.connect(bustype='socketcan', channel=can_interface, bitrate=bitra)
        self.node = self.network.add_node(int(node_id), 'objdict.eds')

    def read_node_state(self) -> str:
        ret = self.node.nmt.state
        return ret
    
    def entry_operable(self) -> None:
        self.network.nmt.state = 'OPERATIONAL'

    def reset_node(self) -> None:
        self.node.nmt.state = 'RESET'
    
    def set_heartbeat(self, value) -> None:
        val = value.to_bytes(4, byteorder='little')
        self.node.sdo.download(0x1017, 0, val)
            
    def read_heartbeat(self) -> str:
        try:
            ret = self.node.nmt.wait_for_heartbeat()
            print("CAN Heartbeat Received")
            return ret
        except Exception as e:
            return e

    def read_error(self):
        try:
            ret = self.node.emcy.wait(timeout=1)
            return ret  
        except Exception as e:
            return e
    
    def power_error_report(self):
        power_state = {
                '0': 'no error',
                '1': 'vcc 24V error',
                '2': 'vcc 5v error',
                '4': 'vcc 3.3v error',
                '8': '2.5v error'
            }
        try:
            ret = self.node.sdo[0x2001].raw
            print("Power Error Report: ", power_state[str(ret)])
            return ret
        except Exception as e:
            return e

    def stateModeSwitch(self) -> None:
        module_state = {
            '0': 'self-inspection',
            '1': 'initialize',
            '2': 'working',
            '3': 'error',
            '4': 'upgrade'
        }
        try:
            ret = self.node.sdo[0x2002].raw
            print("sensor Mode Switch: ", module_state[str(ret)])
            return ret
        except Exception as e:
            return e
            
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
                ret = self.node.sdo[0x2003].raw
                print("read work Mode Switch: ", module_state[str(ret)])
                return ret
            elif operate == "w":
                val = value.to_bytes(1, byteorder='little')
                self.node.sdo.download(0x2003, 0, val)
                return value
        except Exception as e:
            return e

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
            ret = self.node.sdo[0x2004].raw
            print("sensor Mode Switch: ", gpio_state[str(ret)])
            return ret
        except Exception as e:
            return e

    def event_timer(self, operate: str, value=0) -> None:
        """event timer

        Args:
            operate (str): 'r' or 'w'.
            value (int, optional): gpio Read report timer (ms). Defaults to 0.
        """
        try:
            if operate == 'r':
                ret = self.node.sdo[0x1800][5].raw
                return ret
            elif operate == 'w':
                val = value.to_bytes(2, byteorder='little')
                self.node.sdo.download(0x1800, 5, val)
                return value
        except Exception as e:
            return e

    def gpioPower(self, operate: str, value=0) -> None:
        """gpio Power

        Args:
            operate (str): 'r' or 'w'.
            value (int, optional): 0 close 1 open. Defaults to 0.
        """
        try:
            if operate == 'r':
                ret = self.node.sdo[0x2005].raw
                print("GPIO Power Mode: ", ret)
                return ret
            elif operate == 'w':
                val = value.to_bytes(1, byteorder='little')
                self.node.sdo.download(0x2005, 0, val)
                return value
        except Exception as e:
            return e

    def encoderValueRead(self) -> None:
        """Read encoder Value            
        """
        try:
            ret = self.node.sdo[0x2006].raw
            print(f'encoder Value Read: {ret}')
            return ret
        except Exception as e:
            return e

    def encoderPower(self, operate: str, value=0) -> None:
        """encoder Power

        Args:
            operate (str): 'r' or 'w'.
            value (int, optional): 0 close 1 open. Defaults to 0.
        """
        try:
            if operate == 'r':
                ret = self.node.sdo[0x2007].raw
                print("read encoder Power Mode: ", ret)
                return ret
            elif operate == 'w':
                val = value.to_bytes(1, byteorder='little')
                self.node.sdo.download(0x2007, 0, val)
                return value
        except Exception as e:
            return e
    
    def encoder_read_time(self, operate: str, value=0) -> None:
        """设置编码器值的上报周期

        Args:
            operate (str): 'r' or 'w'.
            value (int, optional): gpio Read report timer (ms). Defaults to 0.
        """
        try:
            if operate == 'r':
                ret = self.node.sdo[0x1801][5].raw
                return ret
            elif operate == 'w':
                val = value.to_bytes(2, byteorder='little')
                self.node.sdo.download(0x1801, 5, val)
                return value
        except Exception as e:
            return e

    def Power_5V(self, operate: str, value=0) -> None:
        """Power 5V

        Args:
            operate (str): 'r' or 'w'.
            value (int, optional): 0 close 1 open. Defaults to 0.
        """
        try:
            if operate == 'r':
                ret = self.node.sdo[0x2009].raw
                return ret
            elif operate == 'w':
                val = value.to_bytes(1, byteorder='little')
                self.node.sdo.download(0x2009, 0, val)
                return value
        except Exception as e:
            return e

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
            return e

    def __delattr__(self, __name: str) -> None:
        self.network.sync.stop()
        self.network.disconnect()