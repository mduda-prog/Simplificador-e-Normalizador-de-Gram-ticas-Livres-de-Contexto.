import re
from collections import defaultdict

def parse_grammar():
    grammar = defaultdict(list)
    print("Digite a gramática (linha vazia para terminar):")
    while True:
        line = input().strip()
        if not line:
            break
        head, prods = line.split("->")
        head = head.strip()
        for prod in prods.split("|"):
            grammar[head].append(prod.strip())
    return grammar

def remove_unreachable(grammar, start="S"):
    reachable = set()
    stack = [start]
    while stack:
        symbol = stack.pop()
        if symbol not in reachable:
            reachable.add(symbol)
            for prod in grammar.get(symbol, []):
                for s in prod:
                    if s.isupper():
                        stack.append(s)
    return {k: v for k, v in grammar.items() if k in reachable}

def remove_useless(grammar):
    generating = set()
    changed = True
    while changed:
        changed = False
        for head, prods in grammar.items():
            for prod in prods:
                if all((not s.isupper()) or (s in generating) for s in prod):
                    if head not in generating:
                        generating.add(head)
                        changed = True
    return {k: [p for p in v if all((not s.isupper()) or (s in generating) for s in p)] for k, v in grammar.items() if k in generating}

def remove_empty(grammar):
    nullable = {head for head, prods in grammar.items() if "" in prods or "ε" in prods}
    changed = True
    while changed:
        changed = False
        for head, prods in grammar.items():
            for prod in prods:
                if all(s in nullable or not s.isupper() for s in prod):
                    if head not in nullable:
                        nullable.add(head)
                        changed = True
    new_grammar = defaultdict(list)
    for head, prods in grammar.items():
        for prod in prods:
            if prod not in ["", "ε"]:
                positions = [i for i, s in enumerate(prod) if s in nullable]
                for mask in range(1 << len(positions)):
                    new_prod = list(prod)
                    for i, pos in enumerate(positions):
                        if mask & (1 << i):
                            new_prod[pos] = ""
                    np = "".join(new_prod)
                    if np != prod or prod not in new_grammar[head]:
                        if np != "":
                            new_grammar[head].append(np)
    return dict(new_grammar)

def remove_unit(grammar):
    unit_pairs = set()
    for head in grammar:
        for prod in grammar[head]:
            if prod.isupper():
                unit_pairs.add((head, prod))
    changed = True
    while changed:
        changed = False
        for (A, B) in list(unit_pairs):
            for prod in grammar.get(B, []):
                if prod.isupper() and (A, prod) not in unit_pairs:
                    unit_pairs.add((A, prod))
                    changed = True
    new_grammar = defaultdict(list)
    for head, prods in grammar.items():
        for prod in prods:
            if not prod.isupper():
                new_grammar[head].append(prod)
    for (A, B) in unit_pairs:
        for prod in grammar.get(B, []):
            if not prod.isupper():
                if prod not in new_grammar[A]:
                    new_grammar[A].append(prod)
    return dict(new_grammar)

def chomsky_normal_form(grammar):
    grammar = dict(grammar)
    new_rules = {}
    term_map = {}
    counter = 1
    for head, prods in grammar.items():
        new_rules[head] = []
        for prod in prods:
            if len(prod) > 1:
                new_prod = ""
                for s in prod:
                    if not s.isupper():
                        if s not in term_map:
                            term_var = f"T{counter}"
                            counter += 1
                            term_map[s] = term_var
                            new_rules[term_var] = [s]
                        new_prod += term_map[s]
                    else:
                        new_prod += s
                new_rules[head].append(new_prod)
            else:
                new_rules[head].append(prod)
    done = False
    while not done:
        done = True
        updated = {}
        for head, prods in new_rules.items():
            updated[head] = []
            for prod in prods:
                if len(prod) > 2:
                    done = False
                    first, rest = prod[0], prod[1:]
                    new_var = f"X{counter}"
                    counter += 1
                    updated[head].append(first + new_var)
                    updated[new_var] = [rest]
                else:
                    updated[head].append(prod)
        new_rules = updated
    return new_rules

def greibach_normal_form(grammar):
    gnf = defaultdict(list)
    for head, prods in grammar.items():
        for prod in prods:
            if not prod[0].isupper():
                gnf[head].append(prod)
            else:
                gnf[head].append(prod)  
    return dict(gnf)

def left_factor(grammar):
    new_grammar = defaultdict(list)
    for head, prods in grammar.items():
        prefix_map = defaultdict(list)
        for prod in prods:
            prefix_map[prod[0]].append(prod)
        for prefix, group in prefix_map.items():
            if len(group) > 1:
                new_var = head + "'"
                new_grammar[head].append(prefix + new_var)
                new_grammar[new_var] = [p[1:] if len(p) > 1 else "" for p in group]
            else:
                new_grammar[head].append(group[0])
    return dict(new_grammar)

def remove_left_recursion(grammar):
    new_grammar = defaultdict(list)
    for head, prods in grammar.items():
        recursive = [p for p in prods if p.startswith(head)]
        non_recursive = [p for p in prods if not p.startswith(head)]
        if recursive:
            new_var = head + "'"
            for p in non_recursive:
                new_grammar[head].append(p + new_var)
            for p in recursive:
                new_grammar[new_var].append(p[len(head):] + new_var)
            new_grammar[new_var].append("")
        else:
            new_grammar[head].extend(prods)
    return dict(new_grammar)

def main():
    grammar = parse_grammar()
    grammar = remove_unreachable(grammar)
    grammar = remove_useless(grammar)
    grammar = remove_empty(grammar)
    grammar = remove_unit(grammar)
    print("\nSimplificada:", grammar)
    cnf = chomsky_normal_form(grammar)
    print("\nChomsky:", cnf)
    gnf = greibach_normal_form(grammar)
    print("\nGreibach:", gnf)
    factored = left_factor(grammar)
    print("\nFatorada:", factored)
    no_left_rec = remove_left_recursion(grammar)
    print("\nSem Recursão à Esquerda:", no_left_rec)

if __name__ == "__main__":
    main()
