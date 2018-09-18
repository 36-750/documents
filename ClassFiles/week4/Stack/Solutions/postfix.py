import sys
import re
import itertools


## Parser States

# During parsing, we can be processing input or recording a procedure.
# Label these two states as constants

class State:
    EXECUTING = 0
    RECORDING = 1


## Data Types on the Stack

# Several types of values on the stack:
#   + booleans 
#   + integers (can extend to real numbers later)
#   + symbols (quoted and unquoted)
#   + procedures (executable/unquoted and quoted)
#
# Procedures are sequences of stackable values that are stored in
# a table by their string representation.
# Note: true, false, and nil are reserved symbols, so it's an
# error to define them. 

# Later we will use a class to define stackable values. For now,
# we use a simple tuple (TYPE, value), where the TYPEs are
# predefined constants.

class Type:
    """
    Tags specifying stackable value type

    Use these as constants Type.NUMBER, Type.SYMBOL, Type.PROCEDURE, et cetera.
    We also distinguish quoted symbols Type.QSYMBOL from unquoted
    symbols Type.SYMBOL and quoted (non-executed procedures) from executed
    procedurs. See all_tokens() below.
    """
    NUMBER     = 0
    SYMBOL     = 1
    QSYMBOL    = 2
    BOOLEAN    = 4
    PROCEDURE  = 8
    QPROCEDURE = 16
    MARKER     = 32

def stack_number(value):
    return  (Type.NUMBER, value)

def stack_boolean(value):
    return  (Type.BOOLEAN, value)

def stack_symbol(value):
    return  (Type.SYMBOL, value)

def stack_quoted(value):
    return  (Type.QSYMBOL, value)

def stack_procedure(key, execute=True):
    return  (Type.PROCEDURE if execute else Type.QPROCEDURE, key)


## Input and Parsing Utilities

def issue_error(mesg):
    print("Error: " + mesg, file=sys.stderr)
    
def chain_inputs(new_tokens, orig_tokens):
    """Insert new_tokens in the input before orig_tokens"""
    return itertools.chain(new_tokens, orig_tokens)

def no_exec_while_recording(cmd):
    """
    Decorator that turns off execution of commands when recording procedures

    Apply this to any command functions that are not active when defining
    a procedure, and it will make them simply record their symbols
    back on the stack for later execution.
    """
    def modified_cmd(cmd_name, stack, tokens, state):
        if state == State.RECORDING:
            stack.append(stack_symbol(cmd_name)) # back on the stack
            return (tokens, state)
        else:
            return cmd(cmd_name, stack, tokens, state)
    return modified_cmd


## Built-in Command Definition

def cmd_nil(cmd_name, stack, tokens, state):
    """Does nothing"""
    return (tokens, state)

@no_exec_while_recording
def cmd_pop(cmd_name, stack, tokens, state):
    """Pop the top item off the stack:...A -> ..."""
    stack.pop()
    return (tokens, state)

@no_exec_while_recording
def cmd_dup(cmd_name, stack, tokens, state):
    """Duplicate top item on the stack:...A -> ...AA"""
    top = stack[-1]
    stack.append(top)
    return (tokens, state)

@no_exec_while_recording
def cmd_exch(cmd_name, stack, tokens, state):
    """Exchange top two items on stack: ...BA -> ...AB"""
    top = stack.pop()
    second = stack.pop()
    stack.append(top)
    stack.append(second)
    return (tokens, state)

@no_exec_while_recording
def cmd_copy(cmd_name, stack, tokens, state):
    """... An ... A1 n -> ... An ... A1 An ... A1"""
    return (tokens, state)

@no_exec_while_recording
def cmd_roll(cmd_name, stack, tokens, state):
    """ """
    return (tokens, state)

@no_exec_while_recording
def cmd_index(cmd_name, stack, tokens, state):
    """ """
    return (tokens, state)

@no_exec_while_recording
def cmd_inc(cmd_name, stack, tokens, state):
    """Increment top item on stack: ...A -> ...(A+1)"""
    top_type, top_val = stack.pop()
    if top_type == Type.NUMBER:
        stack.append(stack_number(top_val + 1))
    else:
        issue_error("attempt to increment a non-number")
    return (tokens, state)

@no_exec_while_recording
def cmd_dec(cmd_name, stack, tokens, state):
    """Decrement top item on stack: ...A -> ...(A-1)"""
    top_type, top_val = stack.pop()
    if top_type == Type.NUMBER:
        stack.append(stack_number(top_val - 1))
    else:
        issue_error("attempt to decrement a non-number")
    return (tokens, state)

@no_exec_while_recording
def cmd_add(cmd_name, stack, tokens, state):
    """Add top two items on stack: ...BA -> ...(A+B)"""
    return (tokens, state)

@no_exec_while_recording
def cmd_sub(cmd_name, stack, tokens, state):
    """Subtract top two items on stack: ...BA -> ...(A-B)"""
    return (tokens, state)

@no_exec_while_recording
def cmd_mul(cmd_name, stack, tokens, state):
    """Multiply top two items on stack: ...BA -> ...(A*B)"""
    return (tokens, state)

@no_exec_while_recording
def cmd_eq(cmd_name, stack, tokens, state):
    """Test if top two items are equal: ...AB -> ...x  (x = true or false)"""
    first = stack.pop()
    second = stack.pop()
    # types and values must be equal
    stack.append(stack_boolean(first == second))
    return (tokens, state)

@no_exec_while_recording
def cmd_gt(cmd_name, stack, tokens, state):
    """Indicates whether second item on stack is greater than the first"""
    ftype, first  = stack.pop()  #ATTN: Check types -- need function for this, right?!
    stype, second = stack.pop()

    if ftype == Type.NUMBER and stype == Type.NUMBER:
        stack.append(stack_boolean(second > first))
    else:
        issue_error("Cannot compare non-integers with gt")
    
    return (tokens, state)

@no_exec_while_recording
def cmd_lt(cmd_name, stack, tokens, state):
    return (tokens, state)

@no_exec_while_recording
def cmd_and(cmd_name, stack, tokens, state):
    first_type, first_value   = stack.pop()
    second_type, second_value = stack.pop()

    if first_type != Type.BOOLEAN or second_type != Type.BOOLEAN:
        issue_error("attempt to logical and with non-boolean values")
    else:
        stack.append(stack_boolean(first_value and second_value))
    return (tokens, state)

@no_exec_while_recording
def cmd_or(cmd_name, stack, tokens, state):
    return (tokens, state)

@no_exec_while_recording
def cmd_not(cmd_name, stack, tokens, state):
    top_type, top_value   = stack.pop()

    if top_type != Type.BOOLEAN:
        issue_error("attempt to logical not with non-boolean values")
    else:
        stack.append(stack_boolean(not top_value))
    return (tokens, state)

@no_exec_while_recording
def cmd_ifelse(cmd_name, stack, tokens, state):
    """A '...bool procT procF ifelse' executes procT if bool true else procF"""
    ftype, false_case = stack.pop()
    ttype, true_case  = stack.pop()
    ctype, condition  = stack.pop() # ATTN: should check types here but do that later

    if ctype != Type.BOOLEAN:
        issue_error("condition for ifelse must be a boolean")

    if condition:
        if ftype == Type.PROCEDURE or ftype == Type.QPROCEDURE:
            return (chain_inputs([stack_procedure(true_case)], tokens), state)
        else:
            return (chain_inputs([(ttype, true_case)], tokens), state)
    else:
        if ftype == Type.PROCEDURE or ftype == Type.QPROCEDURE:
            return (chain_inputs([stack_procedure(false_case)], tokens), state)
        else:
            return (chain_inputs([(ftype, false_case)], tokens), state)

@no_exec_while_recording
def cmd_def(cmd_name, stack, tokens, state):
    """Associate a value with a symbol S: ...VS -> ...

    The 

    The symbol's definition is entered into the symbol table.
    This definition is global (can extend to allow globals later).
    """
    stype, symbol = stack.pop()
    vtype, value  = stack.pop()

    if stype != Type.QSYMBOL:
        issue_error("can only define a symbol's value")
    elif vtype == Type.PROCEDURE or vtype == Type.QPROCEDURE:
        symbols[symbol] = stack_procedure(value) # value is key into procedures table
    else:
        symbols[symbol] = (vtype, value)

    return (tokens, state)

def cmd_begin(cmd_name, stack, tokens, state):
    """Defines procedure using items on the stack until a matching end"""

    if state == State.RECORDING:
        index = -1
        marker = (Type.MARKER, None)
        while index > -len(stack) and stack[index] != marker:
            index -= 1
        if stack[index] == marker:
            proc = stack[(index+1):]
            stack[index:] = []
            key = str(proc)
            procedures[key] = proc
            stack.append(stack_procedure(key, execute=False))
        else:
            issue_error("cannot find matching end for procedure")
        return (tokens, State.EXECUTING)
    else:
        issue_error("begin without matching end encountered at top level")
        return (tokens, state)
    
def cmd_end(cmd_name, stack, tokens, state):
    """Start recording a top-level procedure"""
    if state == State.RECORDING:
        stack.append(stack_symbol("end"))
    else:
        stack.append( (Type.MARKER, None) )
    return (tokens, State.RECORDING)

@no_exec_while_recording
def cmd_print(cmd_name, stack, tokens, state):
    """Print the top item on the stack"""
    print(stack[-1][1])
    return (tokens, state)


### Program State

# Note: This code uses global variables, which is ordinarily not
# advisable. But we will see a better approach when we define
# classes and objects in a few weeks.

op_stack = []        # Operations stack for the language computations
reserved = {'nil',   # Reserved symbols
            'false',
            'true',
            'end'}  
symbols  = dict()    # contains symbols defined during operation
procedures = dict()  # maps stringified form to list of stackables

commands = {  # maps command strings to functions implementing them
    'nil':    cmd_nil,
    'pop':    cmd_pop,
    'dup':    cmd_dup,
    'exch':   cmd_exch,
    'copy':   cmd_copy,
    'index':  cmd_index,
    'roll':   cmd_roll,
    'inc':    cmd_inc,
    'dec':    cmd_dec,
    'add':    cmd_add,
    'sub':    cmd_sub,
    'mul':    cmd_mul,
    'eq':     cmd_eq,
    'gt':     cmd_gt,
    'lt':     cmd_lt,
    'and':    cmd_and,
    'or':     cmd_or,
    'not':    cmd_not,
    'ifelse': cmd_ifelse,
    'def':    cmd_def,
    'begin':  cmd_begin,
    'end':    cmd_end,
    'print':  cmd_print,
}


## Parser

#   Comments start with semi-colons and extend to the end of a line
#   Numbers are integers with optional sign but no leading zeros
#   Symbols start with a letter, followed by letters, numbers, select punctuation.
#   A symbol beginning with ' however is not interpreted but left as is.
#   (So 'foo is just a symbol; foo is replaced by its value if any or nil.)
#   Whitespace is ignored between symbols and numbers
#   Erroneous tokens are ignored without comment *for now* (fix later).

# These represent patterns to be matched in the input for various
# types of tokens or other constructs. We filter out comments and illegal
# characters and then match numbers and symbols. All else is managed
# by commands.
comment_pattern = re.compile(r';.*$')       
illegal_pattern = re.compile(r"[^-;A-Za-z0-9:.?%$@# 	']")       
number_pattern  = re.compile(r'(?:-?[1-9]\d*|0)') 
symbol_pattern  = re.compile(r'[A-Za-z][-A-Za-z0-9:.?%$@#]*') 
qsymbol_pattern = re.compile(r"'[A-Za-z][-A-Za-z0-9:.?%$@#]*") 

def all_tokens(filename):
    """Parse source file and generate a stream of stackable tokens."""
    with open(filename, "r") as f:
        for line in f:
            clean_line = re.sub(comment_pattern, '', line)
            clean_line = re.sub(illegal_pattern, '', clean_line)
            tokens = clean_line.split()
            for token in tokens:
                if re.match(number_pattern, token):
                    yield (Type.NUMBER, int(token))
                elif token == "true":
                    yield (Type.BOOLEAN, True)
                elif token == "false":
                    yield (Type.BOOLEAN, False)
                elif re.match(qsymbol_pattern, token):
                    yield (Type.QSYMBOL, token[1:])
                elif re.match(symbol_pattern, token):
                    yield (Type.SYMBOL, token)

def run(filename, stack):
    """Execute code in filename using a specified stack"""
    state = State.EXECUTING         # Executing commands
    tokens = all_tokens(filename)   # Current stream of input tokens

    while True:
        try:
            token = next(tokens)
        except StopIteration:    # no more input tokens
            break 
        #print("Token is : " + str(token)) #ATTN:DEBUG

        ttype, tval = token       # Note: token is a tuple, deconstruct it
        if ttype == Type.SYMBOL:
            if tval in commands:  # command
                try:
                    tokens, state = commands[tval](tval, stack, tokens, state)
                except IndexError:
                    issue_error("Stack error encountered; stack is likely empty")
            elif tval in symbols:
                symbol = symbols[tval]
                stype, svalue = symbol
                if stype == Type.PROCEDURE:
                    # Insert procedure at the head of the next input
                    tokens = chain_inputs(procedures[svalue], tokens)
                else:
                    stack.append(symbol)
        elif ttype == Type.PROCEDURE:
            # Insert procedure
            tokens = chain_inputs(procedures[tval], tokens)
        else: # ttype is NUMBER, BOOLEAN, QSYMBOL, QPROCEDURE 
            stack.append(token)
        #print(stack, state) #ATTN:DEBUG

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run(sys.argv[1], op_stack)   # ATTN: could be fancier here, remember --help
            
