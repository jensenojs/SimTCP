#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description:       :实现对TCP报文段首部格式的模拟
@Date               :2021/06/13 14:20:14
@Author             :Jensen
@version            :1.0
'''

class TcpHeader():
    """
    @description  :
        实现对TCP报文段首部格式的模拟
    ---------
    @Attributes  :
        源端口和目的端口是基于UDP的，这里就先不设计了


        ACK:
        SYN:
        FIN: 上面三个用来做控制连接

        checksum: 这个用来做差错检测

        len：该tcp报文段的大小
    -------
    """
    
    
    def __init__(self):
        self.ACK = 0
        self.SYN = 0
        self.FIN = 0
        
        
        self.len = 0

        self.seq = 0

        self.checksum = 0

        pass





def main():
    '''
    Using to check the function that implementation
    '''
    pass

if __name__ == '__main__':
    main()
