#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description:       :为了实现可靠信息传输所需要的控制逻辑封装的函数
@Date               :2021/06/13 14:07:48
@Author             :Jensen
@version            :1.0
'''


import pickle
from .SimTCPHeader import TcpHeader
from .checksum import cal_checksum
import util
import sys

split = b'split'

def set_chunk_size(header: TcpHeader, waste=100):
    """
    @description  :
        原先所有空间都用来发送目标信息，现在要空出一部分空间给首部信息和分隔符，此外还预留了一小部分的空间
    ---------
    @param  :
        header: 本次发送需要的首部信息
        waste：实操发现好像打包一起发有时候会出现socket报错说数据段过大的情况，所以预留一点空间
    ---------
    @Returns  :
        chunk_size ：决定以多大的尺度对目标文本进行分片
    ---------
    """
    chunk_size = util.MAX_PACKET - sys.getsizeof(header) - sys.getsizeof(split) - waste
    return chunk_size



def pack_tcp_packet(header: TcpHeader, data = None):
    """
    @description  :
        将TCP头部和本次传输的信息进行打包
    ---------
    @param  :
        header: 本次发送所需Tcp头部信息
        data: 待打包的信息
    -------
    @Returns  :
        打好包的TCP报文段
    -------
    """
    if data == None:
        value_data = split
    else:
        value_data = split + data
    header.len = sys.getsizeof(value_data)
    header.checksum = cal_checksum(value_data)
    data = pickle.dumps(header) + value_data
    return data


def unpack_tcp_packet(data: bytes):
    """
    @description  :

    ---------
    @param  :
    
    -------
    @Returns  :
    
    -------
    """
    place = data.find(split)

    if place == -1:
        pass
    else:
        tcpheader_resv = pickle.loads(data[:place])    
        value_data = data[place + len(split): ]
        return tcpheader_resv, value_data, place


        87 173 259 345


        345 - 259 = 86
        259 - 173 = 86
        173 - 87 = 86