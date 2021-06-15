#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description:       :为了实现可靠信息传输所需要的控制逻辑封装的函数, 包括设置信息块的大小，拼包，解包
@Date               :2021/06/13 14:07:48
@Author             :Jensen
@version            :1.0
'''

import pickle
from .SimTCPHeader import TcpHeader
from .checksum import cal_checksum
import util
import sys
from enum import Enum

split = b'split'

class RecvStateEnum(Enum):
    """
    @description  :
        枚举接收方可能会存在的各种状态
    ---------
    @Attributes  :
        1. 期待接受到序列号为0的数据包
        2. 期待接受到序列号为1的数据包 
        3. 校验和不匹配的数据
        4. 收到重复分组 
    -------
    """
    expect_seq0 = 0
    expect_seq1= 1
    checksum_match = 2
    checksum_not_match = 3
    get_repeated_packet = 4
    get_expected_packet = 5

class SendStateEnmu(Enum):
    """
    @description  :
        枚举发送方可能会存在的各种状态
    ---------
    @Attributes  :
    
    -------
    """
    had_send_seq0 = 0
    had_send_seq1 = 1
    send_the_next = 2
    need_to_resend = 3
    checksum_match = 4
    checksum_not_match = 5



def set_chunk_size(waste=100):
    """
    @description  :
        原先所有空间都用来发送目标信息，现在要空出一部分空间给首部信息和分隔符，此外还预留了一小部分的空间
    ---------
    @param  :
        header: 本轮发送需要的首部信息
        waste：实操发现好像打包一起发有时候会出现socket报错说数据段过大的情况，所以预留一点空间
    ---------
    @Returns  :
        chunk_size ：决定以多大的尺度对目标文本进行分片
    ---------
    """
    measure_header_size = TcpHeader()
    chunk_size = util.MAX_PACKET - sys.getsizeof(measure_header_size) - sys.getsizeof(split) - waste
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
        将本次发送的信息解包为TCP头部，有价值的信息
    ---------
    @param  :
        字节流    
    -------
    @Returns  :
        如果是控制报文，则只返回首部信息
        如果是传递信息的报文，则返回首部信息和信息主体 
    -------
    """
    place = data.find(split)

    if place == -1:
        assert 0
    else:
        tcpheader_resv = pickle.loads(data[:place])    
        value_data = data[place + len(split): ]
        if value_data != b'':
            return tcpheader_resv, value_data
        else:
            return tcpheader_resv
