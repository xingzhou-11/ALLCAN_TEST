#!/usr/bin/python3
from enum import Enum, auto
from PyQt5.QtSerialPort import QSerialPortInfo
from PyQt5.QtCore import pyqtSignal, QThread
from threading import Thread
from all_can_s_func import all_can_canopen
import pylink
import canopen
import platform
import time

import threading

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
    
class Up_Signal_set(QThread):
    signal = pyqtSignal(bool)
    signal_type = 0
    signal_msg = ''
    signal_msgs = []

class Text_Signal_set(QThread):
    signal = pyqtSignal(bool)
    signal_type = 0
    signal_msg = ''
    signal_msgs = []

class argument_list():
    device = None
    bitrate = None
    NodeID = None
    VendorId = None
    ProductCode = None
    RevisionVersion = None
    SerNumber = None
    NewNodeID = None
    NewBitrate = None

class StateList(Enum):
    IDLE = 0

    SELECT_BPS=auto()
    FIND_NODE=auto()
    READ_SN=auto()
    SET_ID=auto()
    SET_BITRATE=auto()

    ALL_CAN_S_UP=auto()
    ALL_CAN_A_UP=auto()
    ALL_CAN_Q_UP=auto()

    ALL_CAN_S_TEST=auto()
    ALL_CAN_A_TEST=auto()
    ALL_CAN_Q_TEST=auto()

class Masterstate():
    state = StateList.IDLE
    event_list = []

    Baud_rate = {
        '1000000': 0,
        '800000': 1,
        '500000': 2,
        '250000': 3,
        '125000': 4,
        '100000': 5,
        '50000': 6,
        '20000': 7,
        '10000': 8
    }

    def __init__(self) -> None:
        # threading.Thread.__init__(self)

        self.network = None
        self.node = None

        self.vendor_id = None
        self.product_code = None
        self.revision_version = None
        self.serial_number = None

        self.all_can_func = all_can_canopen()
        self.up_signal_relay = Up_Signal_set()
        self.text_signal_relay = Text_Signal_set()

    def get_state(self):
        return self.state
    
    def get_up_signal_relay(self):
        return self.up_signal_relay
    
    def get_text_signal_relay(self):
        return self.text_signal_relay

    def add_event(self, event):
        self.event_list.append(event)

    def device_up(self, path):
        jlink = pylink.JLink()
                
        jlink.open()

        if jlink.set_tif(pylink.enums.JLinkInterfaces.SWD):
            self.set_Signal('up', 0, ' Jlink设备连接成功')
        else:
            self.set_Signal('up', 0, ' Jlink设备连接失败')
            return True
        
        try:
            jlink.connect('STM32L431RC')
        except Exception as e:
            self.set_Signal('up', 0, 'Jlink设备连接失败')
            print(f'jlink.connect error: {e}')
            return True
                
        if 0 <= jlink.flash_file(f'{path}/all_can_bootloader.bin', 0x08000000):
            self.set_Signal('up', 0, 'all_can_bootloader.bin 烧录成功')
        else:
            self.set_Signal('up', 0, 'all_can_bootloader.bin 烧录失败')
            jlink.close()
            return True
        
        time.sleep(0.1)

        if 0 <= jlink.flash_file(f'{path}/zephyr.signed.bin', 0x0800A000):
            self.set_Signal('up', 0, 'zephyr.signed.bin 烧录成功')
        else:
            self.set_Signal('up', 0, 'zephyr.signed.bin 烧录失败')
            jlink.close()
            return True

        jlink.reset()
        jlink.close()

    def read_device_sn(self):
        Node = argument_list.NodeID

        try:
            node = self.network.add_node(int(Node), 'AllCanS/objdict.eds')
            self.vendor_id = node.sdo[0x1018][1].data
            self.product_code = node.sdo[0x1018][2].data
            self.revision_version = node.sdo[0x1018][3].data
            self.serial_number = node.sdo[0x1018][4].data
        except:
            self.set_Signal('test', 1, '模块未回复SDO 检查ID 波特率')
            time.sleep(0.1)
            return True

        del node
        return False
        
    def set_Signal(self, Tab, msg_type, msg):
        if Tab == 'up':
            if msg_type == 2:
                self.up_signal_relay.signal_msgs = msg
            else:
                self.up_signal_relay.signal_msg = msg

            self.up_signal_relay.signal_type = msg_type
            self.up_signal_relay.signal.emit(True)

        elif Tab == 'test':
            if msg_type == 2:
                self.text_signal_relay.signal_msgs = msg
            else:
                self.text_signal_relay.signal_msg = msg
                print(msg)

            self.text_signal_relay.signal_type = msg_type
            self.text_signal_relay.signal.emit(True)

    def find_emcy(self, id, timeout):
        msg = self.node.emcy.wait(timeout=timeout)
        if msg is not None:
            self.set_Signal('test', 0, f'模块id: {id}, 错误帧: {msg}')
            time.sleep(0.1)
            msg = None

    def find_node(self):
        self.set_Signal('test', 0, '开始扫描')
                    
        try:
            self.network.scanner.reset()
            self.network.scanner.search()
        except:
            self.set_Signal('test', 0, '扫描出错')
            return

        time.sleep(0.5)
        for node_id in self.network.scanner.nodes:
            self.set_Signal('test', 0, f'找到节点: {node_id}')
            time.sleep(0.1)
        
        self.set_Signal('test', 0, '扫描结束')

    def find_device(self):
        device_port = None
        device_list = QSerialPortInfo.availablePorts()

        # 查找设备
        for port in device_list:
            if port.hasProductIdentifier() and port.hasProductIdentifier():
                device_port = port.portName()
        
        if device_port == None:
            self.set_Signal('test', 1, f'检查环境, canable没有连上')
        else:
            if platform.system() == 'Darwin':
                device_port = f'/dev/{device_port}'
            elif platform.system() == 'Windows':
                pass
        
        return device_port
    
    def connit_can(self, status):
        device = self.find_device()
        if device == None: return 
        try:
            self.network = canopen.Network()
            self.network.connect(bustype='slcan', channel=device, bitrate=int(argument_list.bitrate))
            status[0] = False
        except Exception as e:
            self.set_Signal('test', 1, f'canopen初始化失败')
            print(e)

    def check(self):
        if self.network != None: return False
        status = [True]
        t1 = StoppableThread(target=self.connit_can, args=[status,])
        t1.start()
        time_out = time.time() + 5
        while t1.is_alive():
            if time.time() > time_out: t1.stop()
            time.sleep(0.2)

        if status[0]: self.network = None
        return status[0]

    def run(self):
        event = None

        while True:
            if self.state == StateList.IDLE:
                if self.event_list:
                    event = self.event_list.pop(0)

                if event == 'find_node':
                    self.state = StateList.FIND_NODE
                    print('state to FIND NODE')

                elif event == 'read_sn':
                    self.state = StateList.READ_SN
                    print('state to READ SN')

                elif event == 'set_id':
                    self.state = StateList.SET_ID
                    print('state to SET ID')

                elif event == 'all_can_s_up':
                    self.state = StateList.ALL_CAN_S_UP
                    print('state to ALL CAN S UP')

                elif event == 'all_can_a_up':
                    self.state = StateList.ALL_CAN_A_UP
                    print('state to ALL CAN A UP')

                elif event == 'all_can_q_up':
                    self.state = StateList.ALL_CAN_Q_UP
                    print('state to ALL CAN Q UP')

                elif event == 'all_can_s_test':
                    self.state = StateList.ALL_CAN_S_TEST
                    print('state to ALL CAN S TEST')

                elif event == 'all_can_a_test':
                    self.state = StateList.ALL_CAN_A_TEST
                    print('state to ALL CAN A TEST')

                elif event == 'all_can_q_test':
                    self.state = StateList.ALL_CAN_Q_TEST
                    print('state to ALL CAN Q TEST')

                elif event == 'select_bps':
                    self.state = StateList.SELECT_BPS
                    print('state to SELECT BPS')

                elif event == 'set_bitrate':
                    self.state = StateList.SET_BITRATE
                    print('state to SELECT BPS')
            
            elif self.state == StateList.SELECT_BPS:
                if self.network != None:
                    self.network.disconnect()
                
                status = [True]

                t1 = StoppableThread(target=self.connit_can, args=[status,])
                t1.start()

                time_out = time.time() + 5
                while t1.is_alive():
                    if time.time() > time_out: t1.stop()
                    time.sleep(0.2)

                if not status[0]: 
                    self.set_Signal('test', 1, '选择波特率成功')
                else:
                    self.set_Signal('test', 1, '选择波特率失败')

                event = None
                self.state = StateList.IDLE
            
            elif self.state == StateList.FIND_NODE:
                if self.check():
                    pass
                else:
                    self.find_node()

                event = None
                self.state = StateList.IDLE

            elif self.state == StateList.READ_SN:
                if self.check():
                    pass
                else:
                    self.set_Signal('test', 0, '开始读取SN码')
                    time.sleep(0.1)
                    self.set_Signal('test', 0, '...')

                    if self.read_device_sn():
                        pass
                    else:
                        vendorID_str = self.vendor_id.decode('utf-8')[::-1]
                        vendorID_int = self.vendor_id[::-1].hex()
                        productCode_int = self.product_code[::-1].hex()
                        revisionVersion_int = self.revision_version[::-1].hex()
                        serialNumber_int = self.serial_number[::-1].hex()
                    
                        # SN 打印
                        self.set_Signal('test', 2, [
                            f'Vendor-ID str: {vendorID_str}',
                            f'Vendor-ID: {vendorID_int}',
                            f'Product Code: {productCode_int}',
                            f'Revision Version: {revisionVersion_int}',
                            f'Serial Number: {serialNumber_int}',
                            f'读取完成'])

                event = None
                self.state = StateList.IDLE

            elif self.state == StateList.SET_ID:
                if self.check():
                    pass
                else:
                    self.set_Signal('test', 0, '开始更改ID')

                    if argument_list.NodeID == '':
                        self.vendor_id = int(argument_list.VendorId, 16)
                        self.product_code = int(argument_list.ProductCode, 16)
                        self.revision_version = int(argument_list.RevisionVersion, 16)
                        self.serial_number = int(argument_list.SerNumber, 16) 
                        
                    else:
                        if self.read_device_sn():
                            pass
                        else:
                            self.vendor_id = int.from_bytes(self.vendor_id, byteorder='little')
                            self.product_code = int.from_bytes(self.product_code, byteorder='little')
                            self.revision_version = int.from_bytes(self.revision_version, byteorder='little')
                            self.serial_number = int.from_bytes(self.serial_number, byteorder='little')

                    try:
                        ret_bool = self.network.lss.send_switch_state_selective(self.vendor_id, self.product_code, self.revision_version, self.serial_number)
                        node_id = self.network.lss.inquire_node_id()
                    except:
                        ret_bool = None
                    
                    newNode = argument_list.NewNodeID
                    
                    if ret_bool:
                        self.set_Signal('test', 0, f'{node_id} 更改为 {newNode}')
                        self.network.lss.configure_node_id(int(newNode))
                        self.network.lss.store_configuration()
                        self.network.lss.send_switch_state_global(self.network.lss.WAITING_STATE)

                        self.network.nmt.state = 'RESET'
                        node1 = self.network.add_node(int(newNode), 'AllCanS/objdict.eds')

                        try:
                            ret = node1.nmt.wait_for_heartbeat()
                            print('Module status: ', ret)
                            print('CAN Heartbeat Received')
                            self.set_Signal('test', 0, 'ID 修改完成')
                        except:
                            print('CAN Heartbeat Failed')
                            self.set_Signal('test', 0, 'ID 修改失败')

                        del node1
                        node1 = None
                    else:
                        self.set_Signal('test', 0, '未找到设备')

                event = None
                self.state = StateList.IDLE

            elif self.state == StateList.SET_BITRATE:
                if self.check():
                    pass
                else:
                    try:
                        newBitrate = self.Baud_rate[argument_list.NewBitrate]
                    except:
                        self.set_Signal('test', 0, '请输入正确的波特率')
                        event = None
                        self.state = StateList.IDLE
                        continue
                    
                    self.set_Signal('test', 0, '开始更改波特率')

                    if argument_list.NodeID == '':
                        self.vendor_id = int(argument_list.VendorId, 16)
                        self.product_code = int(argument_list.ProductCode, 16)
                        self.revision_version = int(argument_list.RevisionVersion, 16)
                        self.serial_number = int(argument_list.SerNumber, 16)
                    else:
                        if self.read_device_sn():
                            pass
                        else:
                            self.vendor_id = int.from_bytes(self.vendor_id, byteorder='little')
                            self.product_code = int.from_bytes(self.product_code, byteorder='little')
                            self.revision_version = int.from_bytes(self.revision_version, byteorder='little')
                            self.serial_number = int.from_bytes(self.serial_number, byteorder='little')

                    try:
                        ret_bool = self.network.lss.send_switch_state_selective(self.vendor_id, self.product_code, self.revision_version, self.serial_number)
                    except:
                        ret_bool = None
                    
                    if ret_bool:
                        try:
                            print(f'newBitrate: {newBitrate}')
                            self.network.lss.configure_bit_timing(newBitrate)
                            self.network.lss.store_configuration()
                            self.network.lss.send_switch_state_global(self.network.lss.WAITING_STATE)
                        except Exception as e:
                            print(e)
                            self.set_Signal('test', 0, '更改波特率出错')
                            time.sleep(0.1)
                    else:
                        self.set_Signal('test', 0, '未找到设备')
                
                self.network.nmt.state = 'RESET'
                self.set_Signal('test', 0, '更改结束')
                event = None
                self.state = StateList.IDLE

            elif self.state == StateList.ALL_CAN_S_UP:
                self.set_Signal('up', 0, '开始升级ALL-CAN-S')

                if self.device_up('AllCanS'):
                    self.set_Signal('up', 0, 'ALL-CAN-S升级失败')
                else:
                    self.set_Signal('up', 0, 'ALL-CAN-S升级成功')

                event = None
                self.state = StateList.IDLE

            elif self.state == StateList.ALL_CAN_A_UP:
                self.set_Signal('up', 0, '开始升级 ALL-CAN-A')
                time.sleep(0.1)
                self.set_Signal('up', 0, '...')

                if self.device_up('AllCanA'):
                    self.set_Signal('up', 0, 'ALL-CAN-A升级失败')
                else:
                    self.set_Signal('up', 0, 'ALL-CAN-A升级成功')

                event = None
                self.state = StateList.IDLE

            elif self.state == StateList.ALL_CAN_Q_UP:
                self.set_Signal('up', 0, '开始升级 ALL-CAN-Q')
                time.sleep(0.1)
                self.set_Signal('up', 0, '...')

                if self.device_up('AllCanQ'):
                    self.set_Signal('up', 0, 'ALL-CAN-Q升级失败')
                else:
                    self.set_Signal('up', 0, 'ALL-CAN-Q升级成功')

                event = None
                self.state = StateList.IDLE

            elif self.state == StateList.ALL_CAN_S_TEST:
                if self.check():
                    pass
                else:
                    self.set_Signal('test', 0, '开始测试 ALL-CAN-S')
                    time.sleep(0.1)

                    self.find_node()

                    for i in self.network.scanner.nodes:
                        try:
                            self.node = self.network.add_node(i, 'AllCanS/objdict.eds')
                    
                            self.all_can_func.io_output(node=self.node, value=1)

                            if self.all_can_func.io_input(node=self.node) == 1:
                                self.set_Signal('test', 0, f'模块id: {i}, 已打开GPIO输出, GPIO输入读取为1, 测试1通过')
                            else:
                                self.set_Signal('test', 0, f'模块id: {i}, 已打开GPIO输出, GPIO输入读取为0, 测试1不通过')

                            self.find_emcy(id=i, timeout=1)

                            self.all_can_func.io_output(node=self.node, value=0)

                            if self.all_can_func.io_input(node=self.node) == 0:
                                self.set_Signal('test', 0, f'模块id: {i}, 已打开GPIO输出, GPIO输入读取为0, 测试2通过')
                            else:
                                self.set_Signal('test', 0, f'模块id: {i}, 已关闭GPIO输出, GPIO输入读取为1, 测试2不通过')

                            self.find_emcy(id=i, timeout=1)

                            del self.node

                        except Exception as e:
                            self.set_Signal('test', 0, f'模块id: {i}, ALL-CAN-S 测试出错')
                            print(f'ALL-CAN-S TEST ERROR {e}')
                            time.sleep(0.1)

                self.set_Signal('test', 0, '测试结束')
                
                event = None
                self.state = StateList.IDLE

            elif self.state == StateList.ALL_CAN_A_TEST:
                print('开始测试 ALL-CAN-A')
                print('...')
                print('测试完成')
                event = None
                self.state = StateList.IDLE

            elif self.state == StateList.ALL_CAN_Q_TEST:
                if self.check():
                    pass
                else:
                    self.set_Signal('test', 0, '开始测试 ALL-CAN-Q')
                    time.sleep(0.1)

                    self.find_node()

                    for i in self.network.scanner.nodes:
                        try:
                            self.node = self.network.add_node(i, 'AllCanQ/objdict.eds')
                    
                            val = self.all_can_func.read_encoder(self.node)
                            self.set_Signal('test', 0, f'模块id: {i}, 已读取编码器当前值 转动编码器一圈')
                            time.sleep(0.1)
                            self.set_Signal('test', 0, f'五秒后将再次读取编码器值')

                            self.find_emcy(id=i, timeout=1)
                            time.sleep(4)

                            val1 = self.all_can_func.read_encoder(self.node)
                            if abs(val1 - val) > 200:
                                self.set_Signal('test', 0, f'模块id: {i}, 两次细分差值大于200, 角度差大于18度, 测试不通过')
                            else:
                                self.set_Signal('test', 0, f'模块id: {i}, 两次细分差值小于200, 角度差小于18度, 测试通过')

                            self.find_emcy(id=i, timeout=1)

                            del self.node

                        except Exception as e:
                            self.set_Signal('test', 0, f'模块id: {i}, ALL-CAN-Q 测试出错')
                            print(f'ALL-CAN-Q TEST ERROR {e}')
                            time.sleep

                self.set_Signal('test', 0, '测试结束')

                event = None
                self.state = StateList.IDLE
            
            else:
                event = None
                self.state = StateList.IDLE
        
            time.sleep(0.2)
