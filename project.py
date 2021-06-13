"""
Where solution code to project should be written.  No other files should
be modified.
"""

import socket
import io
import time
import typing
import struct
import util
import util.logging

import pickle
import sys
from Transport_connection_management.checksum import cal_checksum
from Transport_connection_management.SimTCPHeader import TcpHeader
from Transport_connection_management.Control import *


'''
使用二进制的split作为切分首部段和信息段的符号, 会参与校验和的计算
'''



def send(sock: socket.socket, data: bytes):
    """
    Implementation of the sending logic for sending data over a slow,
    lossy, constrained network.

    Args:
        sock -- A socket object, constructed and initialized to communicate
                over a simulated lossy network.
        data -- A bytes object, containing the data to send over the network.

    —————————————
    0. add the checksum
        阶段任务：1. 使用Class封装，模拟一个TCP头，与原本信息进行拼接后进行传输
                 2. 在1的基础上，尝试性地添加checksum功能
    —————————————

    —————————————
    1. add the auto request
        阶段任务：1. 发现有覆写的问题，添加停止等待的机制, 同时将首部段和信息段的拼接封装成函数放入Control.py中
                 2. 
    —————————————

    """

    # Naive implementation where we chunk the data to be sent into
    # packets as large as the network will allow, and then send them
    # over the network, pausing half a second between sends to let the
    # network "rest" :)
    logger = util.logging.get_logger("project-sender")
    

    temp = TcpHeader()

    # 设置切片的大小
    chunk_size = set_chunk_size(temp)
    pause = .1

    '''
    将TCP的首部和data进行拼接，添加校验和的功能，然后再发送
    '''

    offsets = range(0, len(data), util.MAX_PACKET)
    for chunk in [data[i: i + chunk_size] for i in offsets]:

        tcpheader_send = TcpHeader()
        # logger.info("the checksum that stole is %d ", tcpheader_send.checksum)
        data = pack_tcp_packet(tcpheader_send, chunk)
        sock.send(data)
        control_data = sock.recv(util.MAX_PACKET)
        tcpheader_resv, _, place = unpack_tcp_packet(control_data)
        if tcpheader_resv.ACK == 1:
            pass
        else:
            assert 0
        logger.info("Sender receive control message from receiver")


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
        
    —————————————
    0. add the checksum
    —————————————

    —————————————
    1. add the auto request
    —————————————

    """
    # tcpheader_resv = TcpHeader()
    logger = util.logging.get_logger("project-receiver")
    # Naive solution, where we continually read data off the socket
    # until we don't receive any more data, and then return.
    num_bytes = 0
    while True:
        data = sock.recv(util.MAX_PACKET)
        if not data:
            break
        
        logger.info("Received %d bytes", len(data))
        tcpheader_resv, value_data, place = unpack_tcp_packet(data)
        logger.info("value data is %s", value_data.decode())
        tcpheader_control = TcpHeader()
        if tcpheader_resv.checksum == cal_checksum(data[place:]):
            dest.write(value_data)
            num_bytes += len(data)
            dest.flush()
            tcpheader_control.ACK = 1
        else:
            pass
        control_data = pack_tcp_packet(tcpheader_control)
        sock.send(control_data)
        logger.info("Receiver send control message to sender!")
        
        
    return num_bytes
