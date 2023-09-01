import canopen
from matplotlib import pyplot as plt
import time
import sys
import numpy as np


network = canopen.Network()
network.connect(bustype='socketcan', channel='can0', bitrate=1000000)
node = network.add_node(1, 'objdict.eds')

def adc_read():
    ret = node.sdo[0x2000].raw
    print("ADC read voltage: ", ret)
    return ret

def power_output(value):
    val = value.to_bytes(1, byteorder='little')
    node.sdo.download(0x6200, 1, val)
    return value

def read_output():
    ret = node.sdo[0x6200][1].raw
    print("output state: ", ret)
    return ret

if __name__ ==  '__main__':
    
    vals = []

    network.nmt.state = 'OPERATIONAL'

    power_output(1)
    
    count = 0

    for i in range(500):
        val = adc_read()
        vals.append(val)
        time.sleep(0.05)

    max_val = np.max(vals)
    min_val = np.min(vals)

    print(f'max: {max_val}')
    print(f'min: {min_val}')

    # print(f'count: {count}')
    # print(f'failure rate: {count/500}')

    plt.scatter(range(500), vals)
    plt.xlabel("count")
    plt.ylabel("value")
    # plt.yticks([i+4955 for i in range(35)])
    plt.show()
