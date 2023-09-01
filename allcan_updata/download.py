#!/usr/bin/env python3
from canopen_program import CANopenBinaryRunner, CANopenProgramDownloader
from core import RunnerConfig
from argparse import ArgumentParser

parser = ArgumentParser(description = 'OTA script')
parser.add_argument('node_id', help = "ID of the current device", type = int)
parser.add_argument('firmware_path', help = "Firmware path to be upgraded", type = str)
parser.add_argument('can_bustype', help = "linux: socketcan ; macos: slcan", type = str)
parser.add_argument('can_interface', help = "linux: can0 ; macos: /dev/tty.usbmodem1411401", type = str)
parser.add_argument('can_bitrate', help = "can bitrate", type = int)

args = parser.parse_args()

con = RunnerConfig(".", ".", None, None, args.firmware_path,
                   None, None, None, None, None, None)
canopenbinrunner = CANopenBinaryRunner(con, args.node_id, confirm_only=False, timeout=20.0,
                                       sdo_timeout=1.0, can_bustype=args.can_bustype,
                                       can_channel=args.can_interface,
                                       can_bitrate=args.can_bitrate)
canopenbinrunner.do_run("flash")
