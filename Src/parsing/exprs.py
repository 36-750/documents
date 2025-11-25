"""A parser demonstrating the language used in the Architecture session.

The basic grammar is

     expr     -> term
               | term SPACE* ("+" | "-") term

     term     -> factor
               | factor SPACE* ("*" | "/") factor

     factor   -> SPACE* (grouping | NUM | var | let)

     grouping -> "(" expr SPACE* ")"

     let      -> "let" SPACE+ IDENT SPACE* "=" expr SPACE* "in" SPACE+ expr SPACE*

     var      -> IDENT

     NUM      -> "-"? [0-9]+
     IDENT    -> ([a-z] | [A-Z])+
     SPACE    -> (" " | "\t" | "\n" | "\f" | "\r")

corresponding to a data type

     data Expr = Num Int
               | Var Ident
               | BinOp Op Expr Expr
               | Let Ident Expr Expr

     type Ident = Text
     data OP = Plus | Minus | Times | Divide

Here are some samples from the language:

     10 * -4 + 3
     1 + 2 - 3 * 4 + 5 / 6 / 0 + 1
     let x = 4 in x + 1
     let x = 4 in let y = 5 in x + y
     let x = 4 in let y = 5 in x + let z = y in z * z
     let x = 4 in (let y = 5 in x + 1) + let z = 2 in z * z
     let x = (let y = 3 in y + y) in x * 3
     let x = let y = 3 in y + y in x * 3
     let x = let y = 1 + let z = 2 in z * z in y + 1 in x * 3

Note: we are using float division here, though that is easily changed.

"""
# pylint: disable=redefined-outer-name, too-many-locals, redefined-builtin
# pylint: disable=missing-class-docstring, missing-function-docstring

from __future__ import annotations

import enum as E   # enum is a combinator

from pyrsistent        import pmap
from pyrsistent.typing import PMap

from combinators import (Parser, Success, Failure, parse, failure,
                         pure, fmap, pipe, fix,
                         seq, follows, followedBy, between,
                         alts, optional, chain,
                         any_char, char, char_in, string, sjoin,
                         space, integer, letters)

bind = pipe
single = any_char

#
# Representation of the Expr data type in classes. The base class is
# the Expr type constructor, and subclasses represent the various
# data constructors.
#

class Expr:
    """The base data type for expressions, corresponding to the type constructor."""

    def __repr__(self):
        cname = self.__class__.__name__
        members = [f'{k}={v}' for k, v in self.__dict__.items()]
        return f'{cname}({", ".join(members)})'

    def pretty(self, level=0, indent=4) -> str:
        """Pretty prints the subtree at this branch."""
        indentation = ' ' * (level * indent)
        return indentation + repr(self)

    def __str__(self):
        return self.pretty()

class Num(Expr):
    "Numbers (signed integers)"
    __match_args__ = ('value',)

    def __init__(self, num: int):
        self.value = num
        super().__init__()

class Var(Expr):
    "Identifiers"
    __match_args__ = ('name',)

    def __init__(self, name: str):
        self.name = name
        super().__init__()

class Op(E.StrEnum):
    PLUS = "+"
    MINUS = "-"
    TIMES = "*"
    DIVIDE = "/"

class Binop(Expr):
    "Binary operator (+, -, *, /) acting on two subexpressions."
    __match_args__ = ('op', 'left', 'right')

    def __init__(self, op: Op, left: Expr, right: Expr):
        self.op = op
        self.left = left
        self.right = right
        super().__init__()

    def pretty(self, level=0, indent=4) -> str:
        indentation = ' ' * (level * indent)
        return f'{indentation}Binop(op=\'{self.op}\')\n{self.left.pretty(level + 1)}\n{self.right.pretty(level + 1)}'

class Let(Expr):
    "A let expression for variable binding."
    __match_args__ = ('var', 'binding', 'value')

    def __init__(self, ident: str, binding: Expr, value: Expr):
        self.var = ident
        self.binding = binding
        self.value = value
        super().__init__()

    def pretty(self, level=0, indent=4) -> str:
        indentation = ' ' * (level * indent)
        return f'{indentation}let {self.var} =\n{self.binding.pretty(level + 1)}\n{indentation}in\n' +\
               f'{self.value.pretty(level + 1)}'


#
# Parser
#

# Helpers

reserved = ['let', 'in']

def var_checked(name: str) -> Parser[Var]:
    "Checks if a name is reserved before constructing a Var parser"
    if name in reserved:
        return failure(f'Reserved word {name} cannot be used as a variable')
    return pure(Var(name))

def as_term(factor_res):
    "Deconstructs a factor with optional multiplicative part."
    left, then = factor_res

    if then is None:
        return left

    op, right = then
    return Binop(op, left, right)

def as_expr(term_res):
    "Deconstructs a term with optional additive part."
    left, then = term_res

    if then is None:
        return left

    op, right = then
    return Binop(op, left, right)


# Basic Component Parsers

add_op = fmap( char_in("+-"), lambda c: Op.PLUS  if c == '+' else Op.MINUS )
mul_op = fmap( char_in("*/"), lambda c: Op.TIMES if c == '*' else Op.DIVIDE )
let_p = string("let")
in_p = string("in")
eq = char('=')
neg = char('-')

ident: Parser[str] = fmap(letters, "".join)
space0: Parser[str] = optional(space, "")   # type: ignore

# Expr Parsers

number: Parser[Num] = fmap( integer, Num )

var: Parser[Var] = bind(ident, var_checked)

def grouping(expr_p: Parser[Expr]) -> Parser[Expr]:
    return between(char('('), expr_p, sjoin(space0, char(')')))

def let(expr_p: Parser[Expr]) -> Parser[Let]:
    return fmap( chain(between(seq(let_p, space), ident, seq(space0, eq)),
                       followedBy(expr_p, seq(space0, in_p)),
                       between(space, expr_p, space0)),
                 lambda es: Let(es[0], es[1], es[2]) )

def factor(expr_p) -> Parser[Expr]:
    return follows(space0, alts(grouping(expr_p), number, let(expr_p), var))

def term(expr_p) -> Parser[Expr]:
    s = follows(space0, seq(mul_op, factor(expr_p)))
    return fmap( seq(factor(expr_p), optional(s)), as_term )

@fix
def expr(expr_p) -> Parser[Expr]:
    s = follows(space0, seq(add_op, term(expr_p)))
    return fmap( seq(term(expr_p), optional(s)), as_expr )


#
# Expr-specific parser
#

def parse_expr(tokens: str):
    """Parses tokens as an expression.

    Returns the result of the parse if successful and all input is consumed.
    Otherwise, returns a failure diagnosing the problem.

    """
    m = parse(tokens, expr)
    match m:
        case Success(result, state):
            if state.available() > 0:
                return Failure("Unused input remains", state.point, {'partial': result})
            return result

        case Failure():
            return m


#
# AST Interpreter
#

class InterpreterError(ValueError):
    pass

def interpret(e: Expr, env=None):
    "An AST interpreter"
    if env is None:
        env = pmap()

    match e:
        case Num(x):
            return x

        case Var(name):
            if name in env:
                return env[name]
            raise InterpreterError(f'Variable {name} used before it is bound to a value.')

        case Binop(op, left, right):
            lval = interpret(left, env)
            rval = interpret(right, env)

            match op:
                case Op.PLUS:
                    return lval + rval

                case Op.MINUS:
                    return lval - rval

                case Op.TIMES:
                    return lval * rval

                case Op.DIVIDE:
                    if rval == 0:
                        raise InterpreterError('Attempt to divide by 0')
                    return lval / rval

        case Let(name, binding, value):
            bound_to = interpret(binding, env)
            return interpret(value, env.set(name, bound_to))

        case other:
            raise InterpreterError(f'Unrecognized constructor {other}')

#
# Bytecode Compiler
#
# We will build a stack-based virtual machine (see stackit for an analogous language).
#
# Each node in the tree will modify the stack in a particular way, with
# an associated *opcode* and corresponding data.
#
# Node     Opcode          Stack
# ---      ------          -----
# Num      Push            ... | (Push value)
# Binop    OpPlus, ...     Compile operands to bytecode on the stack then add the operator code
#                          ... | <left> <right> Op*
# Var      SRef            Var references pushed as (SRef index) with index on the stack
# Let      First           First evaluate binding (with var index), then compile body
#                          with ... | binding body First -> ... | body (takes first of pair)
#
# Thus, each "instruction" adds an item to the stack
#
# We give the opcodes integer values
#
# Push        0
# SRef        1
# First       2
# OpPlus      12     # 4 & 2^(3+k) for k in 0..3
# OpMinus     20
# OpTimes     36
# OpDivide    68
#
# Compiling gives us a byte string.
#
# For simplicity, we will restrict numbers to an even, fixed width. (Default: 16)
#

class CompilerError(ValueError):
    pass

class Opcode(E.IntEnum):
    PUSH = 0
    SREF = 1
    FIRST = 2
    OP_PLUS = 12     # 4 & 2^(3+k) for k in 0..3
    OP_MINUS = 20
    OP_TIMES = 36
    OP_DIVIDE = 68

NUM_BITS = 16
NUM_BYTES = NUM_BITS >> 3
MASK = (1 << NUM_BITS) - 1
NUM_LIMIT = 1 << (NUM_BITS - 1)
LSB_MASK = (1 << (NUM_BITS >> 1)) - 1
MSB_MASK = LSB_MASK << (NUM_BITS >> 1)

def op_of(op: Op) -> int:
    match op:
        case Op.PLUS:
            return Opcode.OP_PLUS
        case Op.MINUS:
            return Opcode.OP_MINUS
        case Op.TIMES:
            return Opcode.OP_TIMES
        case Op.DIVIDE:
            return Opcode.OP_DIVIDE
        case _:
            raise CompilerError(f'Unrecognized op {op}')

def compile(ast: Expr) -> bytes:
    """Compiles an AST into a bytestring of instructions for the stack vm.

    We keep track of a stack pointer into the data stack being built,
    so that we can reference variables, and an instruction pointer
    into the program bytearray being formed here.

    """

    program = bytearray()

    def go(env: PMap[str, int], stack_ptr: int, instruction_ptr: int, e: Expr) -> tuple[int, int]:
        match e:
            case Num(x):
                if x < -NUM_LIMIT or x > NUM_LIMIT - 1:  # Twos complement
                    raise CompilerError(f'Number {x} is greater than allowed bit width.')

                x_bytes = x.to_bytes(NUM_BYTES, 'little', signed=True)

                program.append(Opcode.PUSH)
                program.extend(x_bytes)
                return (stack_ptr + 1, instruction_ptr + 1 + NUM_BYTES)

            case Binop(op, left, right):
                spl, ipl = go(env, stack_ptr, instruction_ptr, left)
                spr, ipr = go(env, spl, ipl, right)
                program.append(op_of(op))
                return (spr - 1, ipr + 1)

            case Var(name):
                if name not in env:
                    raise CompilerError(f'Variable {name} used before it is bound to a value.')
                program.append(Opcode.SREF)
                program.extend(env[name].to_bytes(NUM_BYTES, 'little', signed=True))
                return (stack_ptr + 1, instruction_ptr + 1 + NUM_BYTES)

            case Let(name, binding, value):
                spb, ipb = go(env, stack_ptr, instruction_ptr, binding)
                spbody, ipbody = go(env.set(name, stack_ptr), spb, ipb, value)
                program.append(Opcode.FIRST)
                return (spbody - 1, ipbody + 1)

            case other:
                raise InterpreterError(f'Unrecognized constructor {other}')

    go(pmap(), 0, 0, ast)
    return program


#
# Virtual Machine
#

class VMError(ValueError):
    pass

def run_vm(program: bytes):
    stack = []
    n = len(program)
    p = program

    ip = 0
    while ip < n:
        match Opcode(p[ip]):
            case Opcode.PUSH:
                stack.append(int.from_bytes(p[(ip + 1):(ip + NUM_BYTES)], 'little', signed=True))
                ip += 1 + NUM_BYTES

            case Opcode.SREF:
                addr = int.from_bytes(p[(ip + 1):(ip + NUM_BYTES)], 'little', signed=True)
                stack.append(stack[addr])
                ip += 1 + NUM_BYTES

            case Opcode.FIRST:
                keep = stack.pop()
                _ = stack.pop()
                stack.append(keep)
                ip += 1

            case Opcode.OP_PLUS:
                b = stack.pop()
                a = stack.pop()
                stack.append(a + b)
                ip += 1

            case Opcode.OP_MINUS:
                b = stack.pop()
                a = stack.pop()
                stack.append(a - b)
                ip += 1

            case Opcode.OP_TIMES:
                b = stack.pop()
                a = stack.pop()
                stack.append(a * b)
                ip += 1

            case Opcode.OP_DIVIDE:
                b = stack.pop()
                a = stack.pop()
                if b == 0:
                    raise VMError(f'Attempt to divide by 0: {a} / 0.')
                stack.append(a / b)  # type: ignore
                ip += 1

            case other:
                raise VMError(f'Unrecognized opcode {other}.')

    if len(stack) == 1:
        return stack[0]
    return stack
