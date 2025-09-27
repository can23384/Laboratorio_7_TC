# -*- coding: utf-8 -*-
# Módulo para cargar gramáticas, validar producciones y eliminar ε-producciones.
# Uso de script: python epsilon_removal.py gramatica1.txt [gramatica2.txt ...]
from __future__ import annotations
import sys, re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set, Iterable

Symbol = str
RHS = Tuple[Symbol, ...]
Productions = Dict[Symbol, Set[RHS]]

line_regex = re.compile(
    r'^\s*([A-Z])\s*(?:->|→)\s*(?:ε|[A-Za-z0-9]+)(?:\s*\|\s*(?:ε|[A-Za-z0-9]+))*\s*$'
)

def validate_line(line: str):
    if not line_regex.match(line):
        return False, "La línea no coincide con el formato A -> cuerpo (| cuerpo)*, usando '->' o '→', y cuerpos con [A-Za-z0-9]+ o 'ε'."
    rhs_part = re.split(r'(?:->|→)', line)[1]
    for alt in rhs_part.split('|'):
        alt = alt.strip()
        if 'ε' in alt and alt != 'ε':
            return False, "La alternativa no puede mezclar 'ε' con otros símbolos."
    return True, ""

def parse_line(line: str):
    lhs, rhs = re.split(r'(?:->|→)', line)
    A = lhs.strip()[0]
    alts = []
    for alt in rhs.split('|'):
        s = alt.strip().replace(' ', '')
        if s == 'ε':
            alts.append(tuple())
        else:
            alts.append(tuple(s))
    return A, alts

@dataclass
class Grammar:
    start: Symbol
    prods: Productions = field(default_factory=dict)

    @staticmethod
    def from_lines(lines: Iterable[str]) -> "Grammar":
        cleaned = []
        for raw in lines:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            ok, msg = validate_line(line)
            if not ok:
                raise ValueError(f"Producción mal escrita: {raw!r}\n  Detalle: {msg}")
            cleaned.append(line)

        if not cleaned:
            raise ValueError("El archivo no contiene producciones válidas.")

        start_symbol = cleaned[0].strip()[0]
        prods: Productions = {}

        for line in cleaned:
            A, alts = parse_line(line)
            prods.setdefault(A, set())
            for rhs in alts:
                prods[A].add(rhs)

        return Grammar(start_symbol, prods)

    def to_lines(self, keep_arrow='->') -> List[str]:
        lines = []
        nts = sorted(self.prods.keys())
        for A in nts:
            alts = []
            for rhs in sorted(self.prods[A]):
                if len(rhs) == 0:
                    alts.append('ε')
                else:
                    alts.append(''.join(rhs))
            lines.append(f"{A} {keep_arrow} " + " | ".join(alts))
        return lines

def compute_nullable(grammar: Grammar):
    log = []
    prods = grammar.prods
    nullable: Set[Symbol] = set()

    for A, rhss in prods.items():
        if tuple() in rhss:
            nullable.add(A)
    log.append(f"Inicialmente anulables por ε directo: {sorted(nullable)}")

    changed = True
    it = 0
    while changed:
        changed = False
        it += 1
        new_added = []
        for A, rhss in prods.items():
            if A in nullable:
                continue
            for rhs in rhss:
                if len(rhs) == 0:
                    continue
                if all((ch.isupper() and ch in nullable) for ch in rhs):
                    nullable.add(A)
                    new_added.append(A)
                    changed = True
                    break
        log.append(f"Iteración {it}: añadidos {sorted(new_added)}; Nullable = {sorted(nullable)}")
    return nullable, log

def powerset_bits(positions: List[int]) -> List[int]:
    m = len(positions)
    return [mask for mask in range(1, 1 << m)]

def eliminate_epsilon(grammar: Grammar, verbose=True):
    log = []
    nullable, steps = compute_nullable(grammar)
    log.extend(steps)

    S = grammar.start
    S_nullable = S in nullable
    log.append(f"El símbolo inicial S={S} {'es' if S_nullable else 'NO es'} anulable.")

    new_prods: Productions = {A: set() for A in grammar.prods}

    for A, rhss in grammar.prods.items():
        for rhs in rhss:
            if len(rhs) == 0:
                log.append(f"Omitimos temporalmente {A} -> ε (se agregará si corresponde).")
                continue

            positions = [i for i, ch in enumerate(rhs) if ch.isupper() and ch in nullable]
            log.append(f"Analizando {A} -> {''.join(rhs)}; pos anulables = {positions}")
            new_prods[A].add(rhs)

            for mask in powerset_bits(positions):
                drop = {positions[j] for j in range(len(positions)) if (mask >> j) & 1}
                kept = [ch for i, ch in enumerate(rhs) if i not in drop]
                cand = tuple(kept)
                if len(cand) == 0:
                    if A == S and S_nullable:
                        new_prods[A].add(tuple())
                        log.append(f"   ✓ {A} -> ε (debido a eliminación total y S anulable)")
                    else:
                        log.append(f"   ✗ {A} -> ε (descartada: ε no permitido salvo quizá S)")
                else:
                    if cand not in new_prods[A]:
                        new_prods[A].add(cand)
                        log.append(f"   ✓ {A} -> {''.join(cand)}")


    if S_nullable:
        new_prods.setdefault(S, set()).add(tuple())
    else:
        for A in new_prods:
            if tuple() in new_prods[A]:
                new_prods[A].remove(tuple())

    new_prods = {A: alts for A, alts in new_prods.items() if alts}
    newG = Grammar(grammar.start, new_prods)
    return newG, log

def main(argv):
    if len(argv) < 2:
        print("Uso: python epsilon_removal.py archivo1.txt [archivo2.txt ...]")
        sys.exit(1)

    for path in argv[1:]:
        print("\n============================================")
        print(f"Procesando {path}:")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            G = Grammar.from_lines(lines)

            print("Producciones originales:")
            for ln in G.to_lines():
                print("  ", ln)

            newG, log = eliminate_epsilon(G, verbose=True)
            print("\n== PASOS ==")
            for s in log:
                print(" ", s)

            print("\nGramática SIN ε-producciones (S->ε se conserva solo si S era anulable):")
            for ln in newG.to_lines():
                print("  ", ln)

            out_path = path.replace('.txt', '_sin_epsilon.txt')
            with open(out_path, 'w', encoding='utf-8') as f:
                for ln in newG.to_lines():
                    f.write(ln + '\n')
            print(f"\n➡ Guardado: {out_path}")

        except Exception as e:
            print("ERROR:", e)

if __name__ == '__main__':
    main(sys.argv)