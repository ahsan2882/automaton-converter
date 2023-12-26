from pprint import pprint
from typing import Dict, FrozenSet, List, Union
import re


class DFA:
    def __init__(
        self, states: List[str],
        states_map: Dict[FrozenSet[str], str],
        alphabet: List[str],
        transitions: Dict[FrozenSet[str], str],
        start_state: str,
        accept_states: List[str]
    ) -> None:
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states
        self.states_map = states_map

    def arden_theorem(self, state: str, equations: str) -> str:
        P = Q = ''
        terms = equations.split('+')
        for eq in terms:
            if state in eq:
                P = eq.replace(f'({state})', '')
            else:
                if len(Q) == 0:
                    Q = eq
                else:
                    Q += f"+{eq}"
        return f"({Q})({P})*" if Q != 'ε' else f"({P})*"

    def reduce_eq(self, terms: List[str]) -> str:
        groups: Dict[str, Union[str, List[str]]] = {}
        for term in terms:
            match_state: List[str] = re.findall(r'\((Q\d+)\)', term)
            if match_state:
                common_term = match_state[0]
                if common_term not in groups:
                    groups[common_term] = []
                groups[common_term].append(
                    term.replace(f'({common_term})', '')
                )
            else:
                if '' not in groups:
                    groups[''] = []
                groups[''].append(f"{term}")

        for common_term, group in groups.items():
            groups[common_term] = f"({'|'.join(group)})" if len(
                group) > 1 else group[0]
        reduced_equations = []
        for common_term, group in groups.items():
            new_eq = f"({common_term}){group}" if common_term != '' and group else f"{common_term}{group}"
            reduced_equations.append(new_eq)
        return '+'.join(reduced_equations)

    def convert_to_regular_expression(self) -> str:
        equations: Dict[str, Union[str, List[str]]] = {}
        for state in self.states:
            equations[state] = self.get_equation_for_state(state)
        # reducing all equations in the form Q = Q1a + Q1b + Q2a to Q1(a+b)+Q2a
        print(equations)
        for s in equations:
            equations[s] = self.reduce_eq(equations[s])
        regexpList = []
        for state in self.accept_states:
            regexp = equations[state]
            while 'Q' in regexp:
                match_state: List[str] = re.findall(r'\((Q\d+)\)', regexp)
                if match_state:
                    for match in match_state:
                        if match != state:
                            regexp = regexp.replace(
                                f'({match})', equations[match])
                regexp = self.reduce_eq(regexp.split('+'))
                regexp = self.arden_theorem(state, regexp)
            equations[state] = regexp
            regexpList.append(regexp)
        return '|'.join(regexpList)

    def get_equation_for_state(self, state) -> List[str]:
        equations: List[str] = []
        for transition, next_state in self.transitions.items():
            if next_state == state:
                for item in transition:
                    if 'Q' in item:
                        input_state = item
                    else:
                        transition_symbol = item
                equations.append(f"({input_state}){transition_symbol}")
        if state == self.start_state:
            equations.append('ε')
        return equations
