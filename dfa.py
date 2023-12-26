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
        terms = equations.split('||')
        for eq in terms:
            if state in eq:
                P = eq.replace(f'({state})', '')
            else:
                if len(Q) == 0:
                    Q = eq
                else:
                    Q += f"||{eq}"
        if P != '':
            return f"({Q})({P})*" if Q != 'ε' else f"({P})*"
        return equations

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
            groups[common_term] = f"({'+'.join(group)})" if len(
                group) > 1 else group[0]
        reduced_equations = []
        for common_term, group in groups.items():
            new_eq = f"({common_term}){group}" if common_term != '' and group else f"{common_term}{group}"
            reduced_equations.append(new_eq)
        return '||'.join(reduced_equations)

    def convert_to_regular_expression(self) -> str:
        equations: Dict[str, Union[str, List[str]]] = {
            state: self.get_equation_for_state(state) for state in self.states}
        # reducing all equations in the form Q = Q1a + Q1b + Q2a to Q1(a+b)+Q2a
        print(equations)
        for s in equations:
            equations[s] = self.simplify_eq(
                self.arden_theorem(s, self.reduce_eq(equations[s])))

        regexpList = []
        for state in self.accept_states:
            regexp = equations[state]
            while 'Q' in regexp:
                match_state: List[str] = re.findall(r'\((Q\d+)\)', regexp)
                if match_state:
                    if len(match_state) < len(self.states):
                        for match in match_state:
                            if match != state and equations[match] != 'ε':
                                regexp = regexp.replace(
                                    f'{match}', equations[match])
                            else:
                                regexp = regexp.replace(
                                    f'({match})', '')
                        regexp = self.simplify_eq(regexp)
                        regexp = self.reduce_eq(regexp.split('||'))
                        regexp = self.arden_theorem(state, regexp)
                    else:
                        regexp = self.arden_theorem(state, regexp)
            equations[state] = regexp
            regexp = self.simplify_eq(regexp)
            regexpList.append(regexp)
        return '|'.join(regexpList)

    def check_state_in_exp(self, exp) -> bool:
        return 'Q' in exp and exp in self.states

    def simplify_eq(self, expression: str) -> str:
        states_found: List[str] = []
        closures: Dict = {}
        while '(' in expression:
            start = expression.rfind('(')
            end = expression.find(')', start)
            substring = expression[start+1:end]
            if self.check_state_in_exp(substring):
                states_found.append(substring)
            char_test = expression[end+1:end+2]
            if '||' not in substring:
                if char_test != '*':
                    if self.check_state_in_exp(substring):
                        expression = expression.replace(
                            f"({substring})", f"[{substring}]")
                    else:
                        expression = expression[:start] + \
                            substring + expression[end + 1:]
                else:
                    if substring not in closures.values() and '+' in substring or '*' in substring:
                        index = f'C{len(closures)}'
                        closures[index] = substring
                        expression = expression.replace(
                            f"({substring})", f"[{index}]")
                    else:
                        expression = expression[:start] + \
                            substring + expression[end + 1:]
            else:
                suffix_start = expression.find(')', end-1)
                suffix_end = expression.find(')', end+1)
                if suffix_end == -1:
                    suffix = expression[suffix_start+1:]
                else:
                    suffix = expression[suffix_start+1:suffix_end]
                substring_list = substring.split('||')
                simplified = '||'.join([f"{subs}{suffix}" if subs !=
                                       'ε' else suffix for subs in substring_list])
                expression = expression[:start] + simplified
                # expression = expression_s + \
                #     expression[suffix_end:] if suffix_end != - \
                #     1 else expression_s + expression[suffix_start+1:]
        for s in states_found:
            expression = expression.replace(f"[{s}]", f"({s})")
        for close, closured in closures.items():
            expression = expression.replace(f"[{close}]", f"({closured})")
        return expression

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
