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
split = b'split'



def send(sock: socket.socket, data: bytes):
    """
    Implementation of the sending logic for sending data over a slow,
    lossy, constrained network.

    Args:
        sock -- A socket object, constructed and initialized to communicate
                over a simulated lossy network.
        data -- A bytes object, containing the data to send over the network.

    ————————————
    0. add the checksum
    —————————————

    """

    # Naive implementation where we chunk the data to be sent into
    # packets as large as the network will allow, and then send them
    # over the network, pausing half a second between sends to let the
    # network "rest" :)
    tcpheader_send = TcpHeader()
    logger = util.logging.get_logger("project-sender")
    
    '''
    原本直接发送
    '''
    chunk_size = util.MAX_PACKET - sys.getsizeof(tcpheader_send) - sys.getsizeof(split) - 100
    pause = .1

    '''
    将TCP的首部和data进行拼接，添加校验和的功能，然后再发送
    '''

    offsets = range(0, len(data), util.MAX_PACKET)
    for chunk in [data[i:i + chunk_size] for i in offsets]:

        # 添加切分的符号
        value_data = split + chunk

        tcpheader_send.len = sys.getsizeof(value_data)
        tcpheader_send.checksum = cal_checksum(value_data)
        logger.info("the checksum that stole is %d ", tcpheader_send.checksum)

        data = pickle.dumps(tcpheader_send) + value_data

        sock.send(data)
        logger.info("Sended %d bytes", len(data))
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
        
    ————————————
    0. add the checksum
    —————————————

    """
    tcpheader_resv = TcpHeader()
    logger = util.logging.get_logger("project-receiver")
    # Naive solution, where we continually read data off the socket
    # until we don't receive any more data, and then return.
    num_bytes = 0
    while True:
        data = sock.recv(util.MAX_PACKET)
        if not data:
            break
        

        place = data.find(split)
        logger.info("the place is %d ", place)

        tcpheader_resv = pickle.loads(data[:place])
        logger.info("the checksum that calculated is %d ", cal_checksum(data[place:]))
        assert tcpheader_resv.checksum == cal_checksum(data[place:]), "data went wrong!"
        logger.info("Received %d bytes", len(data))
        value_data = data[place + len(split): ]
        logger.info("value data is %s", value_data.decode())
        dest.write(value_data)
        num_bytes += len(data)
        dest.flush()
    return num_bytes
