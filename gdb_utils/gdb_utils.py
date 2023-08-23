# -*- coding: utf-8 -*-


import gdb
import sys
import inspect

class MyCommand(gdb.Command):
    def __init__(self):
        if int(sys.version[0]) >= 3:
            super().__init__("my_command", gdb.COMMAND_SUPPORT)
        else:
            super(MyCommand, self).__init__("my_command", gdb.COMMAND_SUPPORT)
    def invoke(self, arg, from_tty):
        print("length is : {}".format(len(arg)))
        for i in range(len(arg)):
            print("element is {}".format(arg[i]))
        cv_arg = gdb.string_to_argv(arg)
        print(cv_arg)

class BaseCommand(gdb.Command):
    def __init__(self, cmd_str, cmd_type = gdb.COMMAND_USER):
        super(BaseCommand, self).__init__(cmd_str, cmd_type)

class PointerCommand(BaseCommand):
    '''print pointer arg
Usage: (print_pointer | pp) arg [arg_type]
Output:
    arg : arg type value
    '''
    def __init__(self, cmd_str = "print_pointer", cmd_type = gdb.COMMAND_USER):
        super(PointerCommand, self).__init__(cmd_str, cmd_type)
    
    def invoke(self, argv, from_tty):
        args = gdb.string_to_argv(argv)
        pointer_v = args[0]
        pointer = gdb.parse_and_eval(pointer_v)
        pointer_type = gdb.lookup_type(args[1]).pointer() if len(args) >= 2 else pointer.type
        print("{} : {}".format(pointer, pointer.cast(pointer_type).dereference()))

class AliasPointerCommand(PointerCommand):
    def __init__(self):
        super(AliasPointerCommand, self).__init__("pp")

class PrintTypeCommand(BaseCommand):
    '''print elements types
Usage: (print_type | pt) arg1 arg2 arg3 ...
Output:
    [arg1] type is [type]
    [arg2] type is [type]
    [arg3] type is [type]
    '''
    def __init__(self, cmd_str = "print_type", cmd_type = gdb.COMMAND_USER):
        super(PrintTypeCommand, self,).__init__(cmd_str, cmd_type)

    def invoke(self, argv, from_tty):
        vals = gdb.string_to_argv(argv)
        for val in vals:
            gdb_val = gdb.parse_and_eval(val)
            print("[{}] type is [{}]".format(val, gdb_val.type))

class AliasPrintTypeCommand(PrintTypeCommand):
    def __init__(self):
        super(AliasPrintTypeCommand, self).__init__("pt")

[obj() for name, obj in inspect.getmembers(sys.modules[__name__])
    if inspect.isclass(obj) and issubclass(obj, BaseCommand) and obj is not BaseCommand]

