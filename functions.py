import gdb
import re


class OutputMatches(gdb.Function):
    '''Report whether the output of a given command includes some regex.

    This function is most useful to force existing gdb commands into a
    pipeline. So that one can do 
        pipe ... |  if $_output_contains("info symbol {}", ".text") | ...
    to filter based on whether an address given is in the text segment.

    Note, double quotes are required so that gdb passes the strings across to
    this python function as strings. Single quotes would be treated by gdb as
    quoting a file or function name (see info gdb section 'Program Variables'
    and section 'Examining the Symbol Table').

    Usage:
        $_output_contains(command_string, search_regex) => boolean

    '''
    def __init__(self):
        super(OutputMatches, self).__init__('_output_contains')

    def invoke(self, command, search_pattern):
        gdb_output = gdb.execute(command.string(), False, True)
        if re.search(search_pattern.string(), gdb_output):
            return True
        return False


class WhereIs(gdb.Function):
    '''Return source file and location of a .text address
    
    `$_whereis()` Returns the source file and line number of a .text memory
    address This is useful for piping into other commands, or running `gf` on
    in a vim buffer.

    Usage:
        $_whereis(some_function) => <symbol>:line#

    '''
    def __init__(self):
        super(WhereIs, self).__init__('_whereis')

    def invoke(self, arg):
        pos = gdb.find_pc_line(int(arg.cast(uintptr_t)))
        return pos.symtab.filename + ':' + str(pos.line) 


class FunctionOf(gdb.Function):
    '''Return the function that this address is in.

    This is mainly useful for making nicely printed output (e.g. in a pipeline)

    Usage:
        $_function_of(0x400954)

    '''
    def __init__(self):
        super(FunctionOf, self).__init__('_function_of')

    def invoke(self, arg):
        pos_given = int(arg.cast(uintptr_t))
        orig_block = block = gdb.block_for_pc(pos_given)
        while block.function.name is None:
            if block.superblock:
                block = block.superblock
            else:
                raise gdb.GdbError('Could not find enclosing function of '
                                   '{} ({})'.format(pos_given, arg))

        offset = pos_given - block.start
        offset_str = '+{}'.format(offset) if offset else ''

        return block.function.name + offset_str


OutputMatches()
WhereIs()
FunctionOf()
