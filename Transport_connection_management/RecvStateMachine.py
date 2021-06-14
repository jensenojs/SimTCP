#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description:       :基于有限状态机的思想，完成了receiver的demo
@Date               :2021/06/14 21:34:30
@Author             :Jensen
@version            :1.0
'''

from .SimTCPHeader import TcpHeader
from .Control import *
import socket
import io

class RecvStateMachine:
    """
    @description  :
        Rdt2.0版本中, 接收端仍只具有一个状态, 当分组到达时, 接收方要么回答一个 ACK, 要么回答一个 NAK, 这取决于收到的分组是再受损
        当ACK或者NAK分组丢失的时候, 我们了解到最广泛的解决方案其实是重传, 但是这样会带来一个问题, 接收方不知道它上次发送的ACK/NAK是否被
        发送方正确地接收到, 因此也就无法事先知道接收到的分组是新的分组还是上一次的分组
        
        为确认(ACK/NAK)分组中添加新的字段,对其进行编号,发送方(接收ACK/NAK)对序号进行检查即可
        因此我们就有了修订版的rdt2.1
        
        其实就是维护一个状态变量, 当收到正确的信息的时候，我们回送ACK，然后更改状态

        然后进一步地, 我们应该把检查校验和的逻辑也放进来
    ---------
    @Attributes  :
    -------
    """
    def __init__(self):
        self.current_state = None 

    def __str__(self):
        return "This is the demo of receiver state"

    def get_current_state(self):
        """
        @description  :
            查看当前状态
        ---------
        @param  :
            None 
        -------
        @Returns  :
            期待收到的seq编号的状态
        -------
        """
        # 这里后期把检验的逻辑也给加进来好了 
        if self.current_state != None:
            return self.current_state
        else:
            assert  0, "Have not start yet!"


    def check_the_checksum_of_header(self, tcpheader: TcpHeader, value_data: bytes):
        """
        @description  :
            比较校验和是否相等
        ---------
        @param  :
        
        -------
        @Returns  :
        
        -------
        """        
        if tcpheader.checksum == cal_checksum(split + value_data):
            return RecvStateEnum.checksum_match
        else:
            return RecvStateEnum.checksum_not_match


    def check_the_seq_of_header(self, tcpheader: TcpHeader):
        """
        @description  :
            检查发送包的序列号是否为接收者所期待的，同时完成初始化
        ---------
        @param  :
            发送过来的TcpHeader
        -------
        @Returns  :
            要么返回收到期待包裹的指令
                此时将current_state 转变为下一个expect的包裹
            要么返回收到重复包裹的指令
                此时不改变状态
        -------
        """
        if self.current_state != None:
            if self.current_state.value == tcpheader.seq:
                if self.current_state == RecvStateEnum.expect_seq0:
                    self.current_state = RecvStateEnum.expect_seq1
                else:
                    self.current_state = RecvStateEnum.expect_seq0
                return RecvStateEnum.get_expected_packet
            else:
                return RecvStateEnum.get_repeated_packet
        else:
            '''
            这里其实是假设校验和能确保不重不漏, seq位如果出了错误, 其实不见得能检测出来的
            '''
            if tcpheader.seq == 0:
                self.current_state = RecvStateEnum.expect_seq1
            else:
                self.current_state = RecvStateEnum.expect_seq0
            return RecvStateEnum.get_expected_packet

    def reaction_to_tcp(self, tcpheader_resv: TcpHeader , value_data: bytes):
        """
        @description  :
            处理每一个TCP报文的主函数
                2. 检查TCP首部的校验和，如果错了，将该状态信息返回
                3. 进一步检查序列号，如果不是期望的包裹，则要求重发
        ---------
        @param  :
        
        -------
        @Returns  :
        
        -------
        """
        Result_of_checknum = self.check_the_checksum_of_header(tcpheader_resv, value_data)
        if Result_of_checknum == RecvStateEnum.checksum_not_match:
            return Result_of_checknum
        
        Result_of_seq_of_header = self.check_the_seq_of_header(tcpheader_resv)
        return Result_of_seq_of_header
