#!/usr/bin/env python3
from all_can_func import all_can_canopen
import pytest
import allure
import time
import sys
import os

try:
    test1 = all_can_canopen('can0', 1000000, 1)
except Exception as e:
    if 'No such device' in str(e):
        print("需要连接上CANable")
    sys.exit(0)

@allure.feature('ALL-CAN init')
@allure.tag('commit: 9650868')
def test_ALL_CAN_init():
    ret = ''

    for i in range(2):
        ret = test1.read_heartbeat()

        if 'No boot-up or heartbeat received' in str(ret):
            print('需要执行命令 canup can0 1000000')
            sys.exit(0)
        elif 'None' == ret:
            print('需要连上ALL-CAN并上电')
            sys.exit(0)
        elif 'PRE-OPERATIONAL' == ret:
            print('ALL-CAN进入预操作状态')
            test1.entry_operable()
        elif 'OPERATIONAL' == ret:
            print('ALL-CAN进入操作状态')
        else:
            pass
    
    if 'OPERATIONAL' != ret:
        print('ALL-CAN 无法进入操作状态，测试结束')
        sys.exit(0)

    assert ret == 'OPERATIONAL'

@allure.feature('Modular mode to B')
def test_mode_to_B():
    with allure.step("Write 2 to 0x2003"):
        test1.workModeSwitch('w', value=2)

    with allure.step("Read value from 0x2003"):
        ret = test1.workModeSwitch('r')
        assert ret == 2

@allure.feature('Modular mode to 4')
def test_mode_B_to_4():
    with allure.step("Write 1 to 0x2003"):
        ret = test1.workModeSwitch('w', value=4)
        assert 'Value of parameter written too high' in str(ret)

    with allure.step("Read value from 0x2003"):
        ret = test1.workModeSwitch('r')
        assert ret == 2

@allure.feature('Mode_B GPIO read 24V input')
@pytest.mark.parametrize(
    'number, value',
    [
        (1, 1),
        (2, 2),
        (3, 4),
        (4, 8),
        (5, 16)
    ],
    ids=['GPIO1', 'GPIO2', 'GPIO3', 'GPIO4', 'GPIO5']
)
def test_mode_B_read_gpio(number, value):
    with allure.step("Read value from 0x2004"):
        input(f'需要给 gpio{number} 输入24V, 按下回车继续...')
        ret = test1.gpioRead()
        if number == 5:
            assert 'no IO' in str(ret)
        else:
            assert ret == value

@allure.feature('Mode_A open GPIO1 ~ GPIO5 24V output')
def test_mode_B_gpio_24V_output():
    with allure.step("Write 1 to 0x2005"):
        test1.gpioPower('w', 1)
        assert input('需要测量 GPIO1 ~ GPIO5 是否有24V输出? (y/n): ') == 'y'

@allure.feature('Mode_B close GPIO1 ~ GPIO5 24V output')
def test_mode_B_close_gpio_24V():
    with allure.step("Write 0 to 0x2005"):
        test1.gpioPower('w', 0)
        assert input('需要测量 GPIO1 ~ GPIO5 24V输出是否已经关闭? (y/n): ') == 'y'

@allure.feature('Mode_B open encoder power')
def test_mode_B_open_encoder_Power():
    with allure.step("Write 1 to 0x2007"):
        val = test1.encoderPower('w', 1)
        assert val == 1

@allure.feature('Mode_B read encoder value')
def test_mode_B_read_encoder_value():
    with allure.step("Read value from 0x2006"):
        val = test1.encoderValueRead()
        assert val == 0
    with allure.step("encoder turn one circle, Read value from 0x2006"):
        input('把编码器转一圈, 按下回车继续...')
        test1.encoderValueRead()
        assert input('读到的值是 4000±200 ? (y/n): ') == 'y'

@allure.feature('Mode_B open GPIO1 ~ GPIO4 5V output')
def test_mode_B_gpio_5V_output():
    with allure.step("Write 1 to 0x2009"):
        ret = test1.Power_5V('w', 1)
        assert 'Unsupported access to an object' in str(ret)
        assert input('需要测量 GPIO1 ~ GPIO4 5V 输出是否已经关闭? (y/n): ') == 'y'

@allure.feature('Modular mode to C')
def test_mode_to_C():
    with allure.step("Write 3 to 0x2003"):
        test1.workModeSwitch('w', value=3)

    with allure.step("Read value from 0x2003"):
        ret = test1.workModeSwitch('r')
        assert ret == 3

@allure.feature('Mode_C open GPIO1 ~ GPIO4 5V output')
@pytest.mark.parametrize(
    'number, value',
    [
        (1, 1),
        (2, 2),
        (3, 4),
        (4, 8)
    ],
    ids=['GPIO1', 'GPIO2', 'GPIO3', 'GPIO4']
)
def test_mode_C_gpio_5V_output(number, value):
    with allure.step(f'Write {value} to 0x2009'):
        assert test1.Power_5V('w', value) == value
        assert input(f'需要测量 GPIO{number} 5V 是否已经输出? (y/n): ') == 'y'

@allure.feature('Mode_C close GPIO 5V output')
def test_mode_C_close_gpio_5V():
    with allure.step('Write 0 to 0x2009'):
        assert test1.Power_5V('w', 0) == 0
        assert input('需要测量 GPIO1 ~ GPIO4 5V 是否已经关闭? (y/n): ') == 'y'

@allure.feature('lss sever')
def test_lss_sever():
    with allure.step("read, vendor_id, product_code, revision_version, serial_number"):
        test1.config_node_id('r')
        assert input('vendor_id str == HC ? (y/n): ') == 'y'

    with allure.step("write, new_node_id"):
        new_node_id = input('需要输入新的 node_id (int): ')
        vendor_id = input('复制 Vendor ID (int) 进行输入: ')
        product_code = input('复制 Product Code (int) 进行输入: ')
        revision_version = input('复制 Revision Version (int) 进行输入: ')
        serial_number = input('复制 Serial Number (int) 进行输入: ')
        test1.config_node_id('w', new_node_id=int(new_node_id), vendor_id=int(vendor_id), product_code=int(product_code), revision_version=int(revision_version), serial_number=int(serial_number))

    with allure.step("reset node"):
        test1.reset_node()
        time.sleep(0.5)
        test1.entry_operable()

    with allure.step("read, new_node_id"):
        test2 = all_can_canopen('can0', 1000000, new_node_id)
        ret = test2.config_node_id('r')
        assert ret != False
        assert input('这次打印的信息是不是跟上一次一样 ? (y/n): ') == 'y'
        test2.config_node_id('w', new_node_id=1, vendor_id=int(vendor_id), product_code=int(product_code), revision_version=int(revision_version), serial_number=int(serial_number))
        test2.reset_node()

if __name__ == '__main__':
    name = input('输入报告的名字：')
    
    # 使用 pytest-html 进行测试，生成报告
    pytest.main(['-s', '-q', 'test_all_can_mode_A.py', '--html={name}.html'.format(name=name)])
    
    # 使用 allure-pytest 进行测试，生成报告
    # pytest.main(['-s', '-q','test_all_can_mode_A.py','--clean-alluredir','--alluredir={name}'.format(name=name)])
    # os.system(r"allure generate -c -o allure-report")
