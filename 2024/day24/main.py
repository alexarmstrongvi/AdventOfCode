#!/usr/bin/env python
# Standard library
from collections import defaultdict
import logging
from os import defpath
import time
from typing import NamedTuple, Callable
from graphlib import TopologicalSorter
from collections.abc import Iterable
import operator
from typing import Literal
from itertools import chain
from collections import Counter, deque
from dataclasses import dataclass, field

# 3rd party
from tqdm import tqdm
import networkx as nx
import matplotlib.pyplot as plt

# 1st party
import aoc_utils as aoc

# Globals
log = logging.getLogger('AoC')

################################################################################
# Crossed Wires
#
# Example input:
# x00: 1
# x01: 1
# x02: 1
# y00: 0
# y01: 1
# y02: 0
#
# x00 AND y00 -> z00
# x01 XOR y01 -> z01
# x02 OR y02 -> z02
#
# Part 1:
# Part 2:

def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)

    # Parse
    txt_wires, txt_gates = text.split('\n\n')
    circuit  = parse_circuit(txt_gates.strip().split('\n'))
    wires_in = dict(map(parse_wire, txt_wires.strip().split('\n')))

    # Part 1
    start     = time.perf_counter()
    simulate_circuit(circuit, wires_in)
    bits_z   = get_bits(circuit.wires, 'z')
    z        = bits_to_int(bits_z)
    elapsed  = time.perf_counter() - start
    print(f'Part 1: {z} [t={(elapsed)*1000:.3f}ms]')

    # Part 2 - Requires manual inspection of circuit graph
    start  = time.perf_counter()
    # TODO: Implement something automatic.
    swaps = [
        ('hdt', 'z05'),
        ('gbf', 'z09'),
        ('mht', 'jgt'),
        ('nbf', 'z30'),
    ]
    for w1_key, w2_key in swaps:
        w1 = circuit.wires[w1_key]
        w2 = circuit.wires[w2_key]
        w1.gate_prev, w2.gate_prev = w2.gate_prev, w1.gate_prev
        if w1.gate_prev is not None:
            w1.gate_prev.out = w1
        if w2.gate_prev is not None:
            w2.gate_prev.out = w2
        
    # Generate graph
    fig, _ = visulize_circuit(circuit)
    fig.savefig('adder_circuit.png')
    # Validate ripple adder circuit, raising AssertionError once something is
    # incorect. Then go look at the circuit graph and figure out which wires
    # needs to be switched. Add them to the list above and then re-run to find
    # next error. Repeat until validation succeeeds.
    validate_adder(circuit)
    elapsed  = time.perf_counter() - start
    print(f'Part 2: [t={(elapsed)*1000:.3f}ms]')


################################################################################
Bits = list[bool]
Op   = Callable[[bool, bool], bool]
@dataclass
class LogicGate:
    in1 : 'Wire'
    in2 : 'Wire'
    out : 'Wire'
    op  : Op

    def op_name(self) -> str:
        return self.op.__name__.rstrip('_').upper()

    def __str__(self) -> str:
        return f'{self.in1} {self.op_name()} {self.in2} -> {self.out}'

    def __hash__(self) -> int:
        return hash((self.in1, self.in2, self.out))

@dataclass
class Wire:
    key        : str
    val        : bool | None      = field(default=None)
    gate_prev  : LogicGate | None = field(default=None, repr=False)
    gates_next : tuple[LogicGate,...] | None = field(default=None, repr=False)

    def __str__(self) -> str:
        val = str(int(self.val)) if self.val is not None else '?'
        return f'{self.key}({val})'

    def __hash__(self) -> int:
        return hash(self.key)

class Circuit(NamedTuple):
    gates : list[LogicGate]
    wires : dict[str, Wire]

def simulate_circuit(circuit: Circuit, wires_in: dict[str, bool]) -> None:
    gates_to_sim = deque()
    for wire_key, wire_val in wires_in.items():
        wire     = circuit.wires[wire_key]
        wire.val = wire_val
        for g in wire.gates_next or []:
            gates_to_sim.append(g)

    while len(gates_to_sim) > 0:
        gate = gates_to_sim.popleft()
        try:
            gate.out.val = gate.op(gate.in1.val, gate.in2.val)
        except TypeError:
            gates_to_sim.append(gate)
            continue
        gates_to_sim.extend(gate.out.gates_next or [])

def validate_adder(circuit: Circuit):
    carry = None
    for i in range(45):
        log.info('Validating adder %d', i)
        carry = val_full_adder(
            circuit.wires[f'x{i:02d}'],
            circuit.wires[f'y{i:02d}'],
            carry,
        )
    assert carry is not None and carry.key[0] == 'z'
    
def val_half_adder(w1: Wire, w2: Wire):
    assert w1.gates_next is not None
    assert w2.gates_next is not None
    assert set(w2.gates_next) == set(w1.gates_next)
    g_and, g_xor = w1.gates_next
    if g_and.op_name() == 'XOR' and g_xor.op_name() == 'AND':
        g_and, g_xor = g_xor, g_and
    assert g_and.op_name() == 'AND' and g_and.out.key[0] not in 'xyz'
    assert g_xor.op_name() == 'XOR'
    return g_xor.out, g_and.out

def val_carry_sum(c1: Wire, c2: Wire):
    assert c1.gates_next is not None
    assert c2.gates_next is not None
    assert set(c2.gates_next) == set(c1.gates_next)
    g_or, = c1.gates_next
    assert g_or.op_name() == 'OR' and g_or.out.key[0] not in 'xy'
    return g_or.out

def val_full_adder(x : Wire, y : Wire, carry : Wire | None = None) -> Wire:
    s1, c1 = val_half_adder(x, y)
    if carry is None:
        z = s1
        carry = c1
    else:
        s2, c2 = val_half_adder(s1, carry)
        c3 = val_carry_sum(c1, c2)
        z = s2
        carry = c3
    assert z.key == x.key.replace('x','z')
    assert carry.key[0] not in 'xy'
    return carry

def visulize_circuit(circuit: Circuit):
    # Make graph
    log.info('Creating graph')

    subset_key : dict[int, list[str]] = defaultdict(list)
    layer = 0
    gate_num = defaultdict(int)
    seen = set()
    vis_names = {}
    # Option 2)
    nodes = [circuit.wires['x00'], circuit.wires['y00']]
    while len(nodes) > 0:
        next_layer_nodes = []
        i_adder, i_sublayer = divmod(layer + 2, 4)
        if i_adder < 44 and i_sublayer == 3:
            next_layer_nodes.extend([
                circuit.wires[f'x{i_adder+1:02d}'], 
                circuit.wires[f'y{i_adder+1:02d}'], 
            ])
        for node in nodes:
            if node in seen:
                continue
            seen.add(node)
            if isinstance(node, Wire):
                node_key = node.key
                next_layer_nodes.extend(node.gates_next or [])
                if node.key[0] in 'xyz':
                    node_key = node.key
                elif node.gate_prev.op_name() == 'XOR':
                    node_key = 'S_' + node.key
                else:
                    node_key = 'C_' + node.key
                vis_names[node] = node_key
            else: #if isinstance(node,LogicGate):
                assert isinstance(node,LogicGate)
                if (
                    not (node.in1 in seen and node.in2 in seen) 
                    or node.in1 in nodes
                    or node.in2 in nodes
                ):
                    next_layer_nodes.append(node)
                    seen.remove(node)
                    continue
                op_name = node.op_name()
                node_key = f'{op_name}_{gate_num[op_name]:03d}'
                next_layer_nodes.append(node.out)
                vis_names[node] = node_key
                gate_num[op_name] += 1
            subset_key[layer].append(node_key)
        subset_key[layer].sort()
        log.debug('%02d) %s', layer, subset_key[layer])
        layer += 1
        nodes = next_layer_nodes

    subset_key = {len(subset_key)-layer : nodes for layer, nodes in subset_key.items()}
    G = nx.DiGraph()
    edges = []
    for g in circuit.gates:
        g_key = vis_names[g]
        edges.extend([
            (vis_names[g.in1], g_key),
            (vis_names[g.in2], g_key),
            (g_key, vis_names[g.out]),
        ])
    G.add_edges_from(edges)

    # Visualize
    log.info('Drawing graph')
    fig, ax = plt.subplots(figsize = (5, 200))
    # pos = nx.spring_layout(G)
    pos = nx.multipartite_layout(
        G, 
        subset_key=subset_key,
        align='horizontal',
    )
    nx.draw(
        G, 
        pos, 
        node_color = [
            'b' if n[0] in 'AXO' else 'g' if n[0] == 'z' else 'r' for n in G.nodes()],
        with_labels=True,
        node_size=500, 
        font_size=16,
        # arrowsize=20,
        ax = ax,
    )
    return fig, ax

################################################################################
def parse_circuit(txt_gates):
    gates = []
    wires = {}
    gates_next = defaultdict(list)
    for txt in txt_gates:
        in1_key, in2_key, out_key, op = parse_gate(txt)
        wires[in1_key] = in1 = wires.get(in1_key, Wire(in1_key))
        wires[in2_key] = in2 = wires.get(in2_key, Wire(in2_key))
        wires[out_key] = out = wires.get(out_key, Wire(out_key))
        gate = LogicGate(in1, in2, out, op)
        out.gate_prev = gate
        gates_next[in1_key].append(gate)
        gates_next[in2_key].append(gate)
        gates.append(gate)

    for key, gnext in gates_next.items():
        wires[key].gates_next = tuple(gnext)

    return Circuit(gates, wires)

def parse_wire(line: str) -> tuple[str, bool]:
    key, val = line.split(': ')
    return key, bool(int(val))

def parse_gate(line: str):
    in1, op_name, in2, _, out = line.split()
    op = {
        'AND' : operator.and_,
        'OR'  : operator.or_,
        'XOR' : operator.xor,
    }[op_name]
    return in1, in2, out, op

################################################################################
# Archive
# def simulate_gates(gates, wires):
#     wires = wires.copy()
#     for in1, in2, out, op in sorted_gates(gates):
#         wires[out] = op(wires[in1], wires[in2])
#     return wires
#
# def sorted_gates(gates: Iterable[LogicGate]) -> list[LogicGate]:
#     gate_to_prev_gates = defaultdict(set)
#     for gate in gates:
#         if gate not in gate_to_prev_gates:
#             gate_to_prev_gates[gate] = set()
#         for next_gate in input_wire_to_gates[gate.out]:
#             gate_to_prev_gates[next_gate].add(gate)
#     return list(TopologicalSorter(gate_to_prev_gates).static_order())

# def automatically_find_swaps():
#     bits_x = get_bits(circuit.wires, 'x')
#     bits_y = get_bits(circuit.wires, 'y')
#     x      = bits_to_int(bits_x)
#     y      = bits_to_int(bits_y)
#     bits_z_true = int_to_bits(x+y, n_bits=len(bits_z))
#     assert len(bits_z) == len(bits_z_true)
#     wrong_z_wires = {
#         circuit.wires['z{i:02d}'] for i, val in enumerate(bits_z) 
#         if val != bits_z_true[i]
#     }
#
#     z = simulate_adder(circuit, x, y)
#
#     breakpoint()
#     def swapped_wires_found(candidates):
#         cnt = Counter(c.val for c in candidates)
#         return cnt[0] == cnt[1]
#
#     wrong_wires_all = set()
#     # for wire in wrong_z_wires:
#         
#     
#     def bar(candidates):
#         if swapped_wires_found(candidates):
#             yield candidates.copy()
#         wire = candidates.pop()
#         gate = wire.gate_prev
#         if any(w not in wrong_wires_all for w in gate.wires_out):
#             candidates.add(wire)
#             return
#         for wrong_wires_new in gen_possible_wrong_wires(gate):
#             candidates.update(wrong_wires_new)
#             yield from bar(candidates)
#             for w in wrong_wires_new:
#                 wrong_wires_new.drop(w)
#     bar(wrong_z_wires)
#
#     def foo(wrong_wires) -> Iterable[set[str]]:
#         if swapped_wires_found(wrong_wires):
#             yield set(wrong_wires.keys())
#         out_wire = next(iter(wrong_wires))
#         out_val  = wrong_wires.pop(out_wire)
#         gate     = out_wire_to_gate[out_wire]
#         in1_val  = wires[gate.in1]
#         in2_val  = wires[gate.in2]
#         log.debug('Backtracking to gate %s: %d %s %d -> %d', gate, in1_val, gate.op_name(), in2_val, out_val)
#         inputs   = get_possible_inputs(gate.op, out = 1-out_val)
#         breakpoint()
#         for in1_right, in2_right in inputs:
#             if in1_right != in1_val:
#                 if len(in_wire_to_gates[gate.in1]) > 1: # TODO: Handle this case
#                     log.debug('\tSkipping wire %s that goes to 2+ gates', gate.in1)
#                     continue
#                 else:
#                     log.debug('\tAdding wire %s', gate.in1)
#                     wrong_wires[gate.in1] = in1_val
#             if in2_right != in2_val:
#                 if len(in_wire_to_gates[gate.in2]) > 1: # TODO: Handle this case
#                     log.debug('\tSkipping wire %s that goes to 2+ gates', gate.in2)
#                     continue
#                 else:
#                     log.debug('\tAdding wire %s', gate.in2)
#                     wrong_wires[gate.in2] = in2_val
#
#             breakpoint()
#             yield from foo(wrong_wires)
#
#             if gate.in1 in wrong_wires:
#                 del wrong_wires[gate.in1]
#             if gate.in2 in wrong_wires:
#                 del wrong_wires[gate.in2]
#
#         wrong_wires[out_wire] = out_val
#
#     wrong_wires = min(foo(wrong_z_wires), key=len)
#     swapped_wires = ','.join(sorted(wrong_wires))
#     elapsed   = time.perf_counter() - start
#     print(f'Part 1: {swapped_wires} [t={(elapsed)*1000:.3f}ms]')
#
#     # Part 2
#     # 1) Fin
#     # 2) Find all the wires that contribute to those z wires
#     # 3) Prune all wires that contribute to other correct z wires
#     # 4) For each z wire, swap its inputs until it is correct, then do the next

def simulate_adder(circuit, x: int, y: int) -> int:
    n_bits_x = sum(w.startswith('x') for w in circuit.wires.keys())
    n_bits_y = sum(w.startswith('y') for w in circuit.wires.keys())

    wires = {}
    for i in range(n_bits_x):
        wires[f'x{i:02d}'] = 0
    for i in range(n_bits_y):
        wires[f'y{i:02d}'] = 0

    for i, b in enumerate(int_to_bits(x)):
        wires[f'x{i:02d}'] += b
    for i, b in enumerate(int_to_bits(y)):
        wires[f'y{i:02d}'] += b

    simulate_circuit(circuit, wires)

    z_bits = get_bits(circuit.wires, 'z')
    return bits_to_int(z_bits)

def get_bits(wires: dict[str, Wire], c: Literal['x','y','z']) -> Bits:
    wires_ = sorted((k,v.val) for k,v in wires.items() if k.startswith(c))
    return [(v or False) for _, v in wires_]

def bits_to_int(bits: Bits) -> int:
    return sum(x << i for i, x in enumerate(bits))

def int_to_bits(int_ : int, n_bits: int | None = None) -> Bits:
    bits = list(map(bool,map(int,bin(int_)[2:])))
    if n_bits is not None:
        assert n_bits >= len(bits)
        bits = [False] * (n_bits-len(bits)) + bits
    return bits

# TODO: cache?
def get_possible_inputs(op: Op, out: int) -> list[tuple[bool, bool]]:
    return [
        x for x in ((False,False), (False,True), (True,False), (True,True)) 
        if op(*x) == out
    ]
################################################################################
if __name__ == "__main__":
    main()
