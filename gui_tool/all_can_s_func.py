#!/usr/bin/python3
import canopen
import time
import re
import os

class all_can_canopen():
    
    def __init__(self) -> None:
        pass

    def io_output(self, node, value) -> None:
        val = value.to_bytes(1, byteorder='little')
        node.sdo.download(0x6200, 1, val)
        return value
        
    def io_input(self, node) -> None:
        ret = node.sdo[0x6000][1]
        print(ret.data)
        return ret.raw
    
    def read_encoder(self, node) -> None:
        ret = node.sdo[0x2001]
        print(ret.data)
        return ret.raw
        
    def get_tpdo(self, node) -> None:
        node.tpdo.read()

    def set_tpdo(self, node, index, subindex, trans_type=None, event_timer=10) -> None:
        node.tpdo[4].clear()
        node.tpdo[4].add_variable(index, subindex)
        node.tpdo[4].trans_type = trans_type
        node.tpdo[4].event_timer = event_timer
        node.tpdo[4].enabled = True

        self._node.nmt.state = 'PRE-OPERATIONAL'
        self._node.tpdo.save()
    
    def pdo_received(self, node) -> None:
        node.tpdo[4].add_callback(self.print_speed)
        time.sleep(5)

    def print_speed(self, message):
        print('%s received' % message.name)
        for var in message:
            print('%s = %d' % (var.name, var.raw))
