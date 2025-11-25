# pylint: disable=wildcard-import, unused-wildcard-import, missing-function-docstring, redefined-builtin
# flake8: noqa: F403, F405

from combinators import *
from exprs import *

def run(tokens):
    p = parse_expr(tokens)
    ok = True

    print('program:', tokens)

    print('ast:')
    match p:
        case Failure():
            print(' ', p)
            ok = False
        case _:
            print(p.pretty(1, indent=2))

    print('interpeted:')
    try:
        if ok:
            print(' ', interpret(p))
        else:
            print('  AST not available for interpreter')
    except InterpreterError as e:
        print(f'  Program error {str(e)}')


    print('compiled:')
    try:
        if ok:
            c = compile(p)
            print(' ', c)
        else:
            print('  AST not available for compilation')
    except CompilerError as e:
        print(f'  Compiler error {str(e)}')
        ok = False

    print('run in vm:')
    try:
        if ok:
            print(' ', run_vm(c))
        else:
            print('  No compiler output available')
    except VMError as e:
        print(f'  Virtual Machine error {str(e)}')

    print('-' * 32)


# Simple tests

if __name__ == '__main__':
    run('100')
    run('-16')
    run('32 + 16')
    run('32 - 16')
    run('32 * 16')
    run('32 / 16')
    run('let x = 4 in let y = 5 in x + y')
    run('10 * -4 + 3')
    run('10 * 4 + 3')
    run('let a = 4 in a + 2*(a + 3)')
    run('let x = let y = 1 + let z = 2 in z * z in y + 1 in x * 3')
    run('1 / 0')
    run('let 4')
