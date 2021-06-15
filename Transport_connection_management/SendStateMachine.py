#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description:       :基于有限状态机的思想，完成了sender的demo
@Date               :2021/06/15 10:10:46
@Author             :Jensen
@version            :1.0
'''


from .SimTCPHeader import TcpHeader
from .Control import *


class SendStateMachine:
    """
    @description  :
        发送端的状态机暂时也比较简单，只实现了检测接收方的tcp首部的seq，比较
        当前状态来判断是要重发报文，还是可以发下一个报文。
    ---------
    @Attributes  :
    
    -------
    """
    
    def __init__(self):
        '''
        这个状态记录的是最近一个成功发送的序列号
        '''
        self.current_state = None
        self.seq = None

    def __str__(self):
        return "This is the demo of sender state machine"

    def check_the_checksum_of_header(self, tcpheader_resv: TcpHeader):
        """
        @description  :
            实际上, 由于测试用例里面没有发生位错误的可能, 所以checksum
            的检验本身就是有点鸡肋的，在控制报文中连信息体都没了，那连检测都没地方
            检测，我也没有针对首部进行校验和的计算，所以这里的API该有，但是我就先不实现它
            的功能了，直接pass
        ---------
        @param  :
        
        -------
        @Returns  :
        
        -------
        """        
        pass

    def set_current_state(self, tcpheader_send: TcpHeader):
        """
        @description  :
            每次发送了一个报文之后，都把当前报文的首部传入，更新状态机的状态
        ---------
        @param  :
            本次发送的tcp报文的首部
        -------
        @Returns  :
            None
        -------
        """
        if tcpheader_send.seq == 0:
            self.current_state = SendStateEnmu.had_send_seq0
        elif tcpheader_send.seq == 1:
            self.current_state = SendStateEnmu.had_send_seq1


    def reaction_to_tcp(self, tcpheader_resv: TcpHeader):
        """
        @description  :
            解析接收端发送过来的tcp控制报文首部
            1. 检查校验和
                有这个流程，但是暂时不考虑它
            2. 解读控制报文的ack, 并于当前状态做比较
                如果不相等，那说明上一个发送的包裹并没有成功接受，那就再发送一次
                如果相等，那就说明成功接受了，所以可以发送下一个状态
        ---------
        @param  :
            接收端的控制报文信息
        -------
        @Returns  :
            指示发送端
        -------
        """

        # for now, it just do nothing
        self.check_the_checksum_of_header(tcpheader_resv)

        '''
        这个地方也写得很难看啊...妈的
        '''
        if tcpheader_resv.ACK == self.current_state.value:
            return SendStateEnmu.send_the_next
        else:
            return SendStateEnmu.need_to_resend
        