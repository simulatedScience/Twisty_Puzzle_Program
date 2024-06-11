"""
Convert permutations given in cycle notation to permutation arrays while preserving names.
"""

def parse_cycles(cycles_str):
    # Remove outer parentheses and split the cycles
    cycles_str = cycles_str.strip('()')
    cycles = cycles_str.split(')(')
    return [list(map(int, cycle.split())) for cycle in cycles]

def apply_cycle(permutation, cycle):
    if len(cycle) < 2:
        return
    first = permutation[cycle[0]]
    for i in range(len(cycle) - 1):
        permutation[cycle[i]] = permutation[cycle[i + 1]]
    permutation[cycle[-1]] = first

def convert_to_permutation(cycle_notation, n=60):
    # Initialize permutation as an identity permutation
    permutation = list(range(n))
    # Apply each cycle
    for cycle in cycle_notation:
        apply_cycle(permutation, cycle)
    return permutation

def parse_and_convert(named_permutations, n=60):
    result = {}
    for name, cycles_str in named_permutations.items():
        cycle_notation = parse_cycles(cycles_str)
        permutation = convert_to_permutation(cycle_notation, n)
        result[name] = permutation
    return result

named_permutations = {
    'cycle_4': '(53)(0 4 7 10)(24 27 30 33)',
    'cycle_2_2': '(53)(4 10)(14 20)(27 33)(40 46)',
    'cycle_5': '(53)(6 16 17 13 9)(29 42 43 39 32)',
    'cycle_2_2*': '(53)(2 15)(8 21)(25 41)(31 47)',
    'flip_middle': '(48 53)(49 52)(50 51)',
    'cycle_3': '(53)(8 21 9)(31 47 32)',
}

result = parse_and_convert(named_permutations)
for name, permutation in result.items():
    print(f"'{name}': {permutation},")

