# 环境搭建
## orangepi 系统升级
- 从 [刷机工具下载地址](https://etcher.balena.io/) 下载可执行文件 balenaEtcher-Setup-1.18.4.exe
- 从 [orangepi官网](http://www.orangepi.cn/html/hardWare/computerAndMicrocontrollers/service-and-support/Orange-Pi-3-LTS.html) 下载 ubdutu 镜像
- 使用 balenaEtcher-Setup 升级 orangepi 的 SD 卡中的系统
- 如果 orangepi 的 emmc 中存在系统，orangepi 插上 SD 后启动，在命令行使用命令 `sudo nand-sata-install` 刷新emmc中的系统

<!-- ## 工具环境搭建
- orangepi 安装好系统后，会自带python3.10
- 更新 pip3
    - `pip3 install --upgrade pip`
- 安装pyqt5
    - `pip3 install pyqt5` -->

## 使用方法（orangepi）
- 打开界面
    - 双击 `all_can_test.exe`
- 模块升级
    - orangepi 接上 JLink，JLink 接上 烧写夹，接上 ALL-CAN-S
    - 给 ALL-CAN-S 供电24V
    - 点击界面上的按钮 **ALL-CAN-S升级**，即可对模块进行升级
    - 升级完成后，默认id为 1
- 模块测试
    - orangepi 接上 CANable，CANable 接上 ALL-CAN-S
    - 给 ALL-CAN-S 供电24V
    - 点击界面上的按钮 **ALL-CAN-S测试**，即可对模块进行测试
    - 可以同时测试 10 个 ALL-CAN-S，模块ID不可重复
- 读取模块SN码
    - orangepi 接上 CANable，CANable 接上 ALL-CAN-S
    - 给 ALL-CAN-S 供电24V
    - 点击界面上的按钮 **读取设备SN码**，即可读取模块的SN码
- 更改模块的ID
    - orangepi 接上 CANable，CANable 接上 ALL-CAN-S
    - 给 ALL-CAN-S 供电24V
    - 在输入框中输入期望ID
    - 点击界面上的按钮 **更改设备ID**，即可更改设备的ID

## 当前的工具缺陷
- 在测试前未选择正确的波特率，界面会出现卡死的情况
- 如果点了模块测试或读取SN码或更改设备ID，提示未找到设备或未找到ALL-CAN-S，需要重新连接CANable，重新打开工具界面

## 打包可执行文件
- `pyinstaller all_can_test.spec`

## 打包可执行文件发现的坑
- 在未打包时使用python3执行文件，运行正常，打包后文件报错
    - 可使用 `.\all_can_test.exe > log.txt | type log.txt` 的方法观察输出
    - 打包后文件报错, `Cannot import module can.interfaces.slcan for CAN interface 'slcan': No module named 'can.interfaces.slcan'`
    - 在 `.spec` 文件中操作: `hiddenimports=['can.interfaces.slcan']` 

- 在未打包时使用python3执行文件，运行正常，打包后烧录没有反应
    - 在 `.spec` 文件中操作:
        ```
        datas=[
        ('AllCanA', 'AllCanA'),
        ('AllCanQ', 'AllCanQ'),  
        ('AllCanS', 'AllCanS')
        ],
        ```
    - 将 `AllCanS整个文件夹放入dist文件夹下`

- 让输入框无法输入，但是输入框内的内容能够被复制的方法：
    - 在 `ui_mainwindow` 文件中按下方内容更改
        ```
        # self.TextDisplay.setEnabled(False)
        self.TextDisplay.setReadOnly(True)
        ```
