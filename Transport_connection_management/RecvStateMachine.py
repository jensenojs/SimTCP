#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description:       :基于有限状态机的思想，完成了receiver的demo
@Date               :2021/06/14 21:34:30
@Author             :Jensen
@version            :1.0
'''

from enum import Enum

# 为了能在本路径下运行测试用例，先暂时这么写...
if __name__ == '__main__':
    from SimTCPHeader import TcpHeader
else:
    from .SimTCPHeader import TcpHeader


class RecvStateMachine:
    """
    @description  :
        Rdt2.0版本中, 接收端仍只具有一个状态, 当分组到达时, 接收方要么回答一个 ACK, 要么回答一个 NAK, 这取决于收到的分组是再受损
        当ACK或者NAK分组丢失的时候, 我们了解到最广泛的解决方案其实是重传, 但是这样会带来一个问题, 接收方不知道它上次发送的ACK/NAK是否被
        发送方正确地接收到, 因此也就无法事先知道接收到的分组是新的分组还是上一次的分组
        
        为确认(ACK/NAK)分组中添加新的字段,对其进行编号,发送方(接收ACK/NAK)对序号进行检查即可
        因此我们就有了修订版的rdt2.1
        
        其实就是维护一个状态变量, 当收到正确的信息的时候，我们回送ACK，然后更改状态
    ---------
    @Attributes  :
    -------
    """
    def __init__(self):
        self.current_state = None 

    def __str__(self):
        return "This is the demo of receiver state"

    class StateEnum(Enum):
        expect_seq0 = 0
        expect_seq1= 1

    def get_current_state(self):
        """
        @description  :
            查看当前状态 
        ---------
        @param  :
            None 
        -------
        @Returns  :
            期待收到的seq编号
        -------
        """
        # 这里后期把检验的逻辑也给加进来好了 
        if self.current_state != None:                
            return self.current_state
        else:
            assert  0, "should not reach here"

    def check_the_seq_of_header(self, tcpheader: TcpHeader):
        if self.current_state.value == tcpheader.seq:
            if self.current_state == self.StateEnum.expect_seq0:
                self.current_state = self.StateEnum.expect_seq1
            else:
                self.current_state = self.StateEnum.expect_seq0
            return True 
        else:
            return False

    def set_current_state(self, tcpheader: TcpHeader):
        if self.current_state == None:                                    
            if tcpheader.seq == 0:
                self.current_state = self.StateEnum.expect_seq1
            elif tcpheader.seq == 1:
                self.current_state = self.StateEnum.expect_seq0
            else:
                return False 
        else:                
            if self.check_the_seq_of_header(tcpheader):
                return True
            else:
                return False


def main():
    """
    @description  :
        简单地测试用例，没什么好看的
    ---------
    @param  :
    
    -------
    @Returns  :
    
    -------
    """
    
    
    testheader = TcpHeader()
    testheader.seq = 0
    testreceiver = RecvStateMachine()
    testreceiver.set_current_state(testheader)
    print(testreceiver.get_current_state())
    print("\n\n")
    print("expect 1 but got 0")
    testreceiver.set_current_state(testheader)
    print(testreceiver.get_current_state())

    print("\n\n")

    print("Now we got one")
    testheader.seq = 1
    testreceiver.set_current_state(testheader)
    print(testreceiver.get_current_state())
    print("\n\n")
    print("Show expected 0")    
    print("expect 0 but got 1")
    testreceiver.set_current_state(testheader)
    print(testreceiver.get_current_state())


    print("Now we got 0")
    testheader.seq = 0
    testreceiver.set_current_state(testheader)
    print(testreceiver.get_current_state())
 

if __name__ == '__main__':
    main()
