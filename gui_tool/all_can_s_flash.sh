#!/bin/bash

JLinkExe -device STM32L431RC -CommandFile ./AllCanS/mcuboot.jlink

JLinkExe -device STM32L431RC -CommandFile ./AllCanS/zephyr_signed.jlink
