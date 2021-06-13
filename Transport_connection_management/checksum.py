#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description:       :实现校验和功能
@Date               :2021/06/13 15:23:19
@Author             :Jensen
@version            :1.0
'''

def cal_checksum(data: bytes, byteorder='little'):
    '''
    char_checksum 按字节计算校验和。每个字节被翻译为无符号整数
    @param data: 字节串
    @param byteorder: 大/小端
    '''
    length = len(data)
    checksum = 0
    for i in range(0, length):
        checksum += int.from_bytes(data[i: i+1], byteorder, signed=False)
        checksum &= 0xFF # 强制截断
         
    return checksum

def main():
    # 测试用例
    data = b'0'
    print(cal_checksum(data))


if __name__ == '__main__':
    main()