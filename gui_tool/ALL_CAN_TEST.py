#!/usr/bin/python3
import sys
import time
import pylink
from threading import Thread

from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget

from main_task import StateList, Masterstate, Up_Signal_set, Text_Signal_set, argument_list
from ui_mainwindow import Ui_Form

class MainWindow(QWidget):

    def __init__(self, State) -> None:
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.state = State

        self.up_signal_relay = self.state.get_up_signal_relay()
        self.up_signal_relay.signal.connect(self.up_signal_processing)
        self.ui.UpDisplay.document().setMaximumBlockCount(1000)
        self.ui.ClearDisplay.clicked.connect(self.ClearDisplay)

        self.text_signal_relay = self.state.get_text_signal_relay()
        self.text_signal_relay.signal.connect(self.text_signal_processing)
        self.ui.TextDisplay.document().setMaximumBlockCount(1000)
        self.ui.ClearDisplay_2.clicked.connect(self.ClearDisplay_2)

        self.ui.AllCanSup.clicked.connect(self.AllCanSup)
        self.ui.AllCanAup.clicked.connect(self.AllCanAup)
        self.ui.AllCanQup.clicked.connect(self.AllCanQup)

        self.ui.SelectBPS.currentIndexChanged.connect(self.SelectBPS)
        self.ui.FindNode.clicked.connect(self.Find_Node)
        self.ui.AllCanSTest.clicked.connect(self.AllCanSTest)
        self.ui.AllCanATest.clicked.connect(self.AllCanATest)
        self.ui.AllCanQTest.clicked.connect(self.AllCanQTest)
        self.ui.ReadSN.clicked.connect(self.ReadSN)
        self.ui.ChangeID.clicked.connect(self.ChangeID)
        self.ui.ChangeBitrate.clicked.connect(self.ChangeBitrate)

    def ClearDisplay(self):
        self.ui.UpDisplay.clear()

    def ClearDisplay_2(self):
        self.ui.TextDisplay.clear()
    
    def AllCanSup(self):
        if self.state.get_state() == StateList.IDLE:
            self.state.add_event('all_can_s_up')
        else:
            QMessageBox.warning(self,"警告", '正在运行')

    def AllCanAup(self):
        if self.state.get_state() == StateList.IDLE:
            self.state.add_event('all_can_a_up')
        else:
            QMessageBox.warning(self,"警告", '正在运行')

    def AllCanQup(self):
        if self.state.get_state() == StateList.IDLE:
            self.state.add_event('all_can_q_up')
        else:
            QMessageBox.warning(self,"警告", '正在运行')
    
    def up_signal_processing(self, result):
        """signal processing

        Args:
            result (bool): on-off
            self.up_signal_relay.signal_type == 0, One message display
            self.up_signal_relay.signal_type == 1, Warning message display
            self.up_signal_relay.signal_type == 2, list message display
        """
        if result:
            if 0 == self.up_signal_relay.signal_type:
                self.ui.UpDisplay.appendPlainText(self.up_signal_relay.signal_msg)
                self.up_signal_relay.signal.emit(False)

            elif 1 == self.up_signal_relay.signal_type:
                QMessageBox.warning(self,"警告", self.up_signal_relay.signal_msg)
                self.up_signal_relay.signal.emit(False)

                self.up_signal_relay.signal_msg = 0

            elif 2 == self.up_signal_relay.signal_type:
                for i in self.up_signal_relay.signal_msgs:
                    self.ui.UpDisplay.appendPlainText(i)
                self.up_signal_relay.signal.emit(False)
                self.up_signal_relay.signal_msgs = 0
            
            else:
                self.up_signal_relay.signal.emit(False)

    def SelectBPS(self):
        if self.state.get_state() == StateList.IDLE:
            argument_list.bitrate = self.ui.SelectBPS.currentText()
            self.state.add_event('select_bps')
        else:
            QMessageBox.warning(self,"警告", '正在运行')

    def Find_Node(self):
        if self.state.get_state() == StateList.IDLE:
            argument_list.bitrate = self.ui.SelectBPS.currentText()
            self.state.add_event('find_node')
        else:
            QMessageBox.warning(self,"警告", '正在运行')

    def AllCanSTest(self):
        if self.state.get_state() == StateList.IDLE:
            self.state.add_event('all_can_s_test')
        else:
            QMessageBox.warning(self,"警告", '正在运行')

    def AllCanATest(self):
        if self.state.get_state() == StateList.IDLE:
            self.state.add_event('all_can_a_test')
        else:
            QMessageBox.warning(self,"警告", '正在运行')

    def AllCanQTest(self):
        if self.state.get_state() == StateList.IDLE:
            self.state.add_event('all_can_q_test')
        else:
            QMessageBox.warning(self,"警告", '正在运行')

    def ReadSN(self):
        if self.state.get_state() == StateList.IDLE:
            argument_list.bitrate = self.ui.SelectBPS.currentText()
            argument_list.NodeID = self.ui.NodeID.text()
            if argument_list.bitrate == '' or argument_list.NodeID == '':
                QMessageBox.warning(self,"警告", '需要输入参数')
            else:
                self.state.add_event('read_sn')
        else:
            QMessageBox.warning(self,"警告", '正在运行')

    def ChangeID(self):
        if self.state.get_state() == StateList.IDLE:
            argument_list.bitrate = self.ui.SelectBPS.currentText()
            argument_list.NodeID = self.ui.NodeID.text()
            argument_list.VendorId = self.ui.VendorId.text()
            argument_list.ProductCode = self.ui.ProductCode.text()
            argument_list.RevisionVersion = self.ui.RevisionVersion.text()
            argument_list.SerNumber = self.ui.SerNumber.text()
            argument_list.NewNodeID = self.ui.NewNodeID.text()
            if (argument_list.NodeID or (argument_list.VendorId and argument_list.ProductCode and argument_list.RevisionVersion and argument_list.SerNumber)) and argument_list.NewNodeID:
                self.state.add_event('set_id')
            else:
                QMessageBox.warning(self,"警告", '输入设备ID + 期望ID 或者 SN码 + 期望ID')
        else:
            QMessageBox.warning(self,"警告", '正在运行')

    def ChangeBitrate(self):
        if self.state.get_state() == StateList.IDLE:
            argument_list.bitrate = self.ui.SelectBPS.currentText()
            argument_list.NodeID = self.ui.NodeID.text()
            argument_list.VendorId = self.ui.VendorId.text()
            argument_list.ProductCode = self.ui.ProductCode.text()
            argument_list.RevisionVersion = self.ui.RevisionVersion.text()
            argument_list.SerNumber = self.ui.SerNumber.text()
            argument_list.NewBitrate = self.ui.NewBitrate.text()
            if (argument_list.NodeID or (argument_list.VendorId and argument_list.ProductCode and argument_list.RevisionVersion and argument_list.SerNumber)) and argument_list.NewBitrate:
                self.state.add_event('set_bitrate')
            else:
                QMessageBox.warning(self,"警告", '输入设备ID + 期望波特率 或者 SN码 + 期望波特率')
        else:
            QMessageBox.warning(self,"警告", '正在运行')
    
    def text_signal_processing(self, result):
        """signal processing

        Args:
            result (bool): on-off
            self.text_signal_relay.signal_type == 0, One message display
            self.text_signal_relay.signal_type == 1, Warning message display
            self.text_signal_relay.signal_type == 2, list message display
        """
        if result:
            if 0 == self.text_signal_relay.signal_type:
                self.ui.TextDisplay.appendPlainText(self.text_signal_relay.signal_msg)
                self.text_signal_relay.signal.emit(False)

            elif 1 == self.text_signal_relay.signal_type:
                QMessageBox.warning(self,"警告", self.text_signal_relay.signal_msg)
                self.text_signal_relay.signal.emit(False)

                self.text_signal_relay.signal_msg = 0

            elif 2 == self.text_signal_relay.signal_type:
                for i in self.text_signal_relay.signal_msgs:
                    self.ui.TextDisplay.appendPlainText(i)
                self.text_signal_relay.signal.emit(False)
                self.text_signal_relay.signal_msgs = 0

            else:
                self.text_signal_relay.signal.emit(False)

if __name__ == '__main__':
    state = Masterstate()
    main_task = Thread(target=state.run)
    main_task.daemon = True
    main_task.start()
    app = QApplication(sys.argv)
    window = MainWindow(state)
    window.show()
    sys.exit(app.exec())
