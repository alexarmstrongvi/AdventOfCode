#!/usr/bin/env python
# Standard library
import logging
import re
import time
import io
from itertools import count
import math


from tqdm import tqdm

# 1st party
import aoc_utils as aoc

# Globals
log = logging.getLogger('AoC')

################################################################################
# Chronospatial Computer
#
# Example input:
# Register A: 729
# Register B: 0
# Register C: 0
#
# Program: 0,1,5,4,3,0
#
# Part 1: 4,6,3,5,6,3,5,2,1,0
# Part 2:


def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)
    
    # Solution
    register_text, program_text = text.split('\n\n')
    registers = {
        reg : int(val)
        for reg, val in re.findall(r'Register ([ABC]): (\d+)', register_text)
    }
    program = tuple(map(int, program_text[len('Program: '):].split(',')))

    # Part 1
    start = time.perf_counter()
    output = simulate_computer(registers, program)
    elapsed = time.perf_counter() - start
    print(f'Part 1: {output} [t={elapsed*1000:.3f}ms]')

    # Part 2
    start = time.perf_counter()
    reg_a = find_self_replicating_reg_a(registers, program)
    elapsed = time.perf_counter() - start
    print(f'Part 2: {reg_a} [t={elapsed*1000:.3f}ms]')

################################################################################
def simulate_computer(registers, program) -> tuple[int, ...]:
    # Setup computer state
    PTR = 0
    OUT = []
    REG = registers.copy()

    # Define operations
    def eval_combo(combo_operand):
        return [0, 1, 2, 3, REG['A'], REG['B'], REG['C']][combo_operand]

    def adv(combo_operand: int):
        nonlocal REG
        REG['A'] = REG['A'] >> eval_combo(combo_operand)
    def bdv(combo_operand: int):
        nonlocal REG
        REG['B'] = REG['A'] >> eval_combo(combo_operand)
    def cdv(combo_operand: int):
        nonlocal REG
        REG['C'] = REG['A'] >> eval_combo(combo_operand)

    def bxl(operand: int):
        nonlocal REG
        REG['B'] = REG['B'] ^ operand
    def bst(combo_operand: int):
        nonlocal REG
        REG['B'] = eval_combo(combo_operand) & 0b111
    def bxc(_):
        nonlocal REG 
        REG['B'] = REG['B'] ^ REG['C']

    def jnz(operand: int):
        nonlocal PTR
        PTR = operand if REG['A'] > 0 else PTR + 2
    def out(combo_operand: int):
        nonlocal OUT
        OUT.append(eval_combo(combo_operand) & 0b111)

    OPS = [adv, bxl, bst, jnz, bxc, out, bdv, cdv]

    # Simulate computer
    while 0 <= PTR < len(program)-1:
        opcode  = program[PTR]
        operand = program[PTR+1]
        op      = OPS[opcode]

        # DEBUG
        # dbg_prg = list(f' {" ".join(map(str,program))}')
        # dbg_prg[PTR*2] = '>'
        # log.debug('A=%10s B=%10s C=%10s | %s | %s(%d) | %s', 
        #     *tuple(map(to_oct, REG.values())), 
        #     ''.join(dbg_prg),
        #     op.__name__, operand,
        #     ','.join(map(str,OUT)),
        # )

        op(operand)
        if op.__name__ != 'jnz':
            PTR += 2

    return tuple(OUT)

def find_self_replicating_reg_a(registers, program):
    registers['A'] = 0
    output = []
    while (nth_output := rfind_first_diff(program, output)) is not None:
        registers['A'] += 0o10 ** nth_output
        output = simulate_computer(registers, program)
        log.info(f'A = %{len(program)+1}s : %s', oct(registers['A']), output)
    return registers['A']

def rfind_first_diff(l1, l2) -> int | None:
    if len(l2) == 0:
        return len(l1)-1
    assert len(l1) == len(l2)
    n = len(l1)
    for i in reversed(range(n)):
        if l1[i] != l2[i]:
            return i
    return None
################################################################################
def to_str(out: io.StringIO) -> str:
    out.seek(0)
    return out.read()

def to_oct(x: int) -> str:
    return oct(x)[2:]

################################################################################
if __name__ == "__main__":
    main()
