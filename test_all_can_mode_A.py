#!/usr/bin/env python3
from all_can_func import all_can_canopen
import pytest
import allure
import time
import os

test1 = all_can_canopen('can0', 1000000, 1)

test1.reset_node()
time.sleep(0.5)
test1.entry_operable()

@allure.feature('Modular mode to A')
@allure.tag('commit: 9650868')
def test_mode_to_A():
    with allure.step("Write 1 to 0x2003"):
        test1.workModeSwitch('w', value=1)

    with allure.step("Read value from 0x2003"):
        ret = test1.workModeSwitch('r')
        assert ret == 1

@allure.feature('GPIO read 24V input')
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
def test_read_gpio(number, value):
    with allure.step("Read value from 0x2004"):
        input(f'gpio{number} input, press Enter to continue...')
        ret = test1.gpioRead()
        assert ret == value

@allure.feature('Mode_A open GPIO1 ~ GPIO5 24V output')
def test_mode_A_gpio_24V_output():
    with allure.step("Write 1 to 0x2005"):
        test1.gpioPower('w', 1)
        assert input('GPIO1 ~ GPIO5 24V Output correct? (T/F): ') == 'T'

@allure.feature('Mode_A close GPIO1 ~ GPIO5 24V output')
def test_mode_A_close_gpio_24V():
    with allure.step("Write 0 to 0x2005"):
        test1.gpioPower('w', 0)
        assert input('GPIO1 ~ GPIO5 No 24V output? (T/F): ') == 'T'

@allure.feature('Mode_A open encoder power')
def test_mode_A_open_encoder_Power():
    with allure.step("Write 1 to 0x2007"):
        val = test1.encoderPower('w', 1)
        assert val == False

@allure.feature('Mode_A read encoder value')
def test_mode_A_read_encoder_value():
    with allure.step("Read value from 0x2006"):
        val = test1.encoderValueRead()
        assert val == False

@allure.feature('Mode_A open GPIO1 ~ GPIO4 5V output')
def test_mode_A_gpio_5V_output():
    with allure.step("Write 1 to 0x2009"):
        val = test1.Power_5V('w', 0x0F)
        assert val == False
        assert input('No 5V output? (T/F): ') == 'T'

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
        assert input(f'GPIO{number} 5V output correct? (T/F): ') == 'T'

@allure.feature('Mode_C close GPIO 5V output')
def test_mode_C_close_gpio_5V():
    with allure.step('Write 0 to 0x2009'):
        assert test1.Power_5V('w', 0) == 0
        assert input('GPIO1 ~ GPIO4 No 5V output? (T/F): ') == 'T'

allure.feature('lss sever')
def test_lss_sever():
    with allure.step("read, vendor_id, product_code, revision_version, serial_number"):
        test1.config_node_id('r')
        assert input('vendor_id str == HC ? (T/F): ') == 'T'

    with allure.step("write, new_node_id"):
        new_node_id = input('new_node_id (int): ')
        vendor_id = input('Vendor ID (int): ')
        product_code = input('Product Code (int): ')
        revision_version = input('Revision Version (int): ')
        serial_number = input('Serial Number (int): ')
        test1.config_node_id('w', new_node_id=int(new_node_id), vendor_id=int(vendor_id), product_code=int(product_code), revision_version=int(revision_version), serial_number=int(serial_number))

    with allure.step("reset node"):
        test1.reset_node()
        time.sleep(0.5)
        test1.entry_operable()

    with allure.step("read, new_node_id"):
        test2 = all_can_canopen('can0', 1000000, new_node_id)
        ret = test2.config_node_id('r')
        assert ret != False
        assert input('The message is the same as last time ? (T/F): ') == 'T'
        test2.config_node_id('w', new_node_id=1, vendor_id=int(vendor_id), product_code=int(product_code), revision_version=int(revision_version), serial_number=int(serial_number))
        test2.reset_node()

if __name__ == '__main__':
    pytest.main(['-s', '-q','test_all_can_mode_A.py','--clean-alluredir','--alluredir=allure-results'])
    os.system(r"allure generate -c -o allure-report")
