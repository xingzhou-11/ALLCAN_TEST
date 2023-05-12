#!/usr/bin/env python3
import time
import can
import canopen
from argparse import ArgumentParser

parser = ArgumentParser(description = 'canio arguments')
parser.add_argument("can_interface", help = "can0 or can1 ...", type = str)
parser.add_argument("can_bitrate", help = "can bitrate", type = str)
parser.add_argument("now_node_id", help = "can id of the device", type = str)
parser.add_argument("--new_node_id", help = "lss node ID", type = str, required=False)

class all_can_canopen():
    
    can_interface = parser.parse_args().can_interface
    bitra = int(parser.parse_args().can_bitrate)
    now_node_id = parser.parse_args().now_node_id
    new_node_id = int(parser.parse_args().new_node_id)

    vendor_id = 0
    product_code = 0
    revision_version = 0
    serial_number = 0
    
    def __init__(self) -> None:
        self.network = canopen.Network()
        self.network.connect(bustype='socketcan', channel=self.can_interface, bitrate=self.bitra)
        self.node = self.network.add_node(int(self.now_node_id), 'objdict.eds')

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

    def config_node_id(self, operate: str, node_id=1) -> None:
        try:
            if operate == 'r':
                self.vendor_id = self.node.sdo[0x1018][1]
                self.product_code = self.node.sdo[0x1018][2]
                self.revision_version = self.node.sdo[0x1018][3]
                self.serial_number = self.node.sdo[0x1018][4]

                print("Vendor-ID str: ", self.vendor_id.get_data().decode('utf-8'))[::-1]
                print("Vendor-ID int: ", self.vendor_id.raw)
                print("Product Code int: ", self.product_code.raw)
                print("Revision Version int: ", self.revision_version.raw)
                print("Serial Number int: ", self.serial_number.raw)

            elif operate == 'w':
                ret_bool = self.network.lss.send_switch_state_selective(self.vendor_id.raw, 
                                                                        self.product_code.raw, 
                                                                        self.revision_version.raw, 
                                                                        self.serial_number.raw)

                if ret_bool:
                    node_id = self.network.lss.inquire_node_id()

                    self.network.lss.configure_node_id(self.new_node_id)
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


def test_start():
    test1 = all_can_canopen()
    test1.reset_node()
    time.sleep(0.5)
    test1.entry_operable()

    print('开始测试')
    print('模式切换')
    input('按下任意键继续...')
    # 模式切换
    test1.workModeSwitch('w', 1)
    test1.workModeSwitch('r')
    time.sleep(0.5)

    test1.workModeSwitch('w', 2)
    test1.workModeSwitch('r')
    time.sleep(0.5)

    test1.workModeSwitch('w', 3)
    test1.workModeSwitch('r')
    time.sleep(0.5)

    print('读取GPIO')
    input('回车一次读取一次gpio, 输入 break 退出gpio读取')
    # 读取GPIO
    test1.gpioRead()

    # 设置GPIO上报
    test1.event_timer('w', 0)

    # GPIO输出控制
    test1.gpioPower('w', 1)
    test1.gpioPower('r', 0)

    # # 使能编码器
    test1.encoderPower('w', 1)

    # # 设置编码器值上报周期
    test1.encoder_read_val('w', 1000)

    while True:
        print(test1.node.sdo[0x2006].raw)
        time.sleep(1)

    # LSS服务
    # test1.config_node_id()

if __name__ == "__main__":
    test_start()
