#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description:       :
@Date               :2021/06/13 14:07:48
@Author             :Jensen
@version            :1.0
'''

# 打包
def make_tcp_packet(data: bytes, usage: int):
    """
    @description  :
        将TCP头部和本次传输的信息进行打包
    ---------
    @param  :
        data: 待打包的信息
        usage: 暂定0是控制报文，1是传递报文
    -------
    @Returns  :
        打好包的TCP报文段
    -------
    """
    
    
    pass