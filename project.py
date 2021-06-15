"""
Where solution code to project should be written.  No other files should
be modified.
"""

import socket
import io
import time
import util
import util.logging

from Transport_connection_management.SendStateMachine import SendStateMachine
from Transport_connection_management.RecvStateMachine import RecvStateMachine
from Transport_connection_management.SimTCPHeader import TcpHeader
from Transport_connection_management.Control import *

'''
—————————————
0. add the checksum
    i. 使用Class封装，模拟一个TCP头，与原本信息进行拼接后进行传输
    ii. 在i的基础上，尝试性地添加checksum功能
—————————————

—————————————
1. add the auto request
    i. 发现有覆写的问题，添加停止等待的机制（的基础框架）
    ii. 同时将首部段和信息段的拼接封装成函数放入Control.py中
    iii. 将bug进行了修复, 至此，已经完成了Rdt2.0的功能，虽然目前框架代码还不能对它做出检测就是了
—————————————

—————————————
2. aiming to solve: what if the ack/nak got wrong （Rdt2.2）/ what if the package lost (Rdt3.0)?
    i. 设定重置时间, 如果没有收到，则通过1.i搭建起来的反馈框架，发出需要的请求
        a. 引入序列号, ack进行处理
            同时跨越2.1，对ack采用累计确认机制
        b. 如何计算RTT，什么时候决定要求重传，遇到重复分组后该怎么办
            序列号虽然能够解决这个问题，但是实现的接口上需要设计
—————————————

'''



def send(sock: socket.socket, data: bytes):
    """
    Implementation of the sending logic for sending data over a slow,
    lossy, constrained network.

    Args:
        sock -- A socket object, constructed and initialized to communicate
                over a simulated lossy network.
        data -- A bytes object, containing the data to send over the network.

    """

    logger = util.logging.get_logger("project-sender")
    chunk_size = set_chunk_size()
    pause = .1

    '''
    0. 将TCP的首部和data进行拼接，添加校验和的功能
    1. 添加停止等待框架
    2. 添加有限状态机, 使用序列号功能
    3. 
    '''

    '''
    三次握手！
    '''

    state_meachine = SendStateMachine()

    # 缓存上一次发送的TCP报文，以准备第二次发送

    # 完成发送报文的初始化
    tcpheader_send = TcpHeader()
    tcpheader_send.seq = 0


    offsets = range(0, len(data), chunk_size)
    for chunk in [data[i: i + chunk_size] for i in offsets]:
        data = pack_tcp_packet(tcpheader_send, chunk)

        # ------------
        # 使用状态机对其进行描述
        sock.send(data)

        # last_sended_data = data
        state_meachine.set_current_state(tcpheader_send)

        control_data = sock.recv(util.MAX_PACKET)
        tcpheader_resv = unpack_tcp_packet(control_data)

        state = state_meachine.reaction_to_tcp(tcpheader_resv)

        if state == SendStateEnmu.need_to_resend:
            while True:
                sock.send(data)
                logger.info(state)
                
                control_data = sock.recv(util.MAX_PACKET)
                tcpheader_resv = unpack_tcp_packet(control_data)
                state = state_meachine.reaction_to_tcp(tcpheader_resv)

                if state == SendStateEnmu.send_the_next:
                    break
        else:
            # 修改序列号, 不然接受方是不愿意收的
            if tcpheader_send.seq == 0:
                tcpheader_send.seq = 1
            else:
                tcpheader_send.seq = 0
            logger.info(state)
        # ------------


        logger.info("Pausing for %f seconds", round(pause, 2))
        time.sleep(pause)





def recv(sock: socket.socket, dest: io.BufferedIOBase) -> int:
    """
    Implementation of the receiving logic for receiving data over a slow,
    lossy, constrained network.

    Args:
        sock -- A socket object, constructed and initialized to communicate
                over a simulated lossy network.

    Return:
        The number of bytes written to the destination.

    """
    # tcpheader_resv = TcpHeader()
    logger = util.logging.get_logger("project-receiver")
    # Naive solution, where we continually read data off the socket
    # until we don't receive any more data, and then return.
    num_bytes = 0

    state_machine = RecvStateMachine()

    while True:

        '''
        三次握手！
        '''

        data = sock.recv(util.MAX_PACKET)
        if not data:
            break

        logger.info("Received %d bytes", len(data))

        tcpheader_control = TcpHeader()
        # ------------

        tcpheader_resv, value_data = unpack_tcp_packet(data)

        '''
        if tcpheader_resv.checksum == cal_checksum(split+value_data):
            dest.write(value_data)
            num_bytes += len(data)
            dest.flush()
            tcpheader_control.ACK = 1
        else:
            pass
        control_data = pack_tcp_packet(tcpheader_control)
        sock.send(control_data)

        '''
        state = state_machine.reaction_to_tcp(tcpheader_resv, value_data)
        
        # 如果成功接受，才会更改ack的值，并且进一步地将数据写入io
        tcpheader_control.ACK = state_machine.get_ack()
        if state == RecvStateEnum.get_expected_packet:
            dest.write(value_data)
            num_bytes += len(data)
            dest.flush()
        else:
        # 收到了重复发送的包裹，可能是因为之前回送的ack丢失了，所以什么都不做再发一次就好了
            pass

        control_data = pack_tcp_packet(tcpheader_control)
        sock.send(control_data)

        logger.info("Receiver send control message to sender!")

        # ------------


    return num_bytes
