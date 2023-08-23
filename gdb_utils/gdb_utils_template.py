# -*- coding: utf-8 -*-


import gdb


class MyCommand(gdb.Command):
    def __init__(self):
        super().__init__("my_command",
                gdb.COMMAND_SUPPORT)
    def invoke(self, arg, from_tty):
        print("length is : {}".format(len(arg)))
        for i in range(len(arg)):
            print("element is {}".format(arg[i]))
        cv_arg = gdb.string_to_argv(arg)
        print(cv_arg)

class PointerCommand(gdb.Command):
    def __init__(self):
        super().__init__('print_pointer', gdb.COMMAND_USER)

    def invoke(self, argv, from_tty):
        pointer_v, type_str = gdb.string_to_argv(argv)
        pointer = gdb.parse_and_eval(pointer_v)
        pointer_type = gdb.lookup_type(type_str).pointer()
        print("{} : {}".format(pointer, pointer.cast(pointer_type).dereference()))

class PrintTypeCommand(gdb.Command):
    def __init__(self):
        super().__init__("print_type", gdb.COMMAND_USER)

    def invoke(self, argv, from_tty):
        vals = gdb.string_to_argv(argv)
        for val in vals:
            gdb_val = gdb.parse_and_eval(val)
            print("[{}] type is [{}]".format(val, gdb_val.type))
PrintTypeCommand()
MyCommand()
PointerCommand()

# convenience function
# dsl实现
'''
# mv2.gdb
# 使用python...end语句块，使得我们可以在gdb的DSL文件里面编写python代码。
python
import os
# 1. 继承gdb.Function
class FindBreakpoint(gdb.Function):
    "Find specific breakpoint with location"
    def __init__(self):
        # 2. 注册函数名字'findBreakpoint'
        super(self.__class__, self).__init__('findBreakpint')

    def invoke(self, location):
        # 3. 不要忘了，invoke方法接受的参数是gdb.Value，所以后面我通过
        # string方法来获得字符串值。
        bps = gdb.breakpoints() # 获取全部断点
        if bps is None:
            raise gdb.GdbError('No breakpoints')
        for bp in bps:
            # 由于断点的location属性返回的是绝对路径，把它转成相对路径
            if os.path.relpath(bp.location) == location.string():
                # 4. convenience function需要返回值，gdb会把它包装成gdb.Value类型
                return bp.number
        raise gdb.GdbError("Specific breakpoint can't be found.")

# 5. 最后一步，向gdb会话注册该函数
FindBreakpoint()
end

define mv
    if $argc == 2
        # 调用它的时候不要忘记'$'前缀
        set $i = $findBreakpint($arg0)
        delete $i
        # 看到我在上面耍的一个trick吗？
        # findBreakpint返回的是一个gdb.Value，
        # 需要把它绑定到DSL变量上，才能在DSL中使用。
        break $arg1
'''

''' 内存泄露定位
# malloc_free.py
from collections import defaultdict, namedtuple
import atexit
import time
import gdb


Entry = namedtuple('Entry', ['addr', 'bt', 'timestamp', 'size'])
MEMORY_POOL = {}
MEMORY_LOST = defaultdict(list)

def comm(event):
    if isinstance(event, gdb.SignalEvent): return
    # handle BreakpointEvent
    for bp in event.breakpoints:
        if bp.number == 1:
            addr = str(gdb.parse_and_eval('p'))
            bt = gdb.execute('bt', to_string=True)
            timestamp = time.strftime('%H:%M:%S', time.localtime())
            size = int(gdb.parse_and_eval('size'))
            if addr in MEMORY_POOL:
                MEMORY_LOST[addr].append(MEMORY_POOL[addr])
            MEMORY_POOL[addr] = Entry(addr, bt, timestamp, size)
        elif bp.number == 2:
            addr = gdb.parse_and_eval('p')
            if addr in MEMORY_POOL:
                del MEMORY_POOL[addr]
    gdb.execute('c')


def dump_memory_lost(memory_lost, filename):
    with open(filename, 'w') as f:
        for entries in MEMORY_LOST.values():
            for e in entries:
                f.write("Timestamp: %s\tAddr: %s\tSize: %d" % (
                        e.timestamp, e.addr, e.size))
                f.write('\n%s\n' % e.bt)


atexit.register(dump_memory_lost, MEMORY_LOST, '/tmp/log')
# Write to result file once signal catched
gdb.events.stop.connect(comm)

gdb.execute('set pagination off')
gdb.execute('b my_malloc') # breakpoint 1
gdb.execute('b my_free') # breakpoint 2
gdb.execute('c')
'''
