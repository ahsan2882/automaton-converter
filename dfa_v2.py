import re
from typing import Dict, FrozenSet, List, Tuple, Union


class DFA:
    def __init__(
        self, states: List[str],
        alphabet: List[str],
        transitions: Dict[FrozenSet[str], str],
        start_state: str,
        accept_states: List[str],
        states_map: Dict[FrozenSet[str], str] = {}
    ) -> None:
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states
        self.states_map = states_map
        self.__check_symbol_in_transitions()

    def __check_symbol_in_transitions(self):
        for transition in self.transitions:
            (_, symbol) = self.__get_transition_state_symbol(transition)
            if symbol not in self.alphabet:
                raise Exception(f"Invalid character {symbol} in transitions.")

    def __arden_theorem(self, state: str, equations: str,) -> str:
        equation = self.__reduce_equation_for_state(
            equations.split('||'), state)
        P = Q = ''
        terms = equation.split('||')
        for eq in terms:
            if state in eq:
                P = eq.replace(f'({state})', '')
            else:
                Q = eq if len(Q) == 0 else Q + f"||{eq}"
        if P != '':
            return f"({Q})({P})*" if Q != 'ε' else f"({P})*"
        return equation

    def __reduce_equation_for_state(self, terms: List[str], state_match: str) -> str:
        grouped_expression = ''
        reduced_equations = []
        for term in terms:
            if '|' in term:
                term = term.replace('|', '||')
                term = self.__simplify_equation(term)
            if state_match in term:
                match_state = re.findall(r'\((Q\d+)\)', term)
                if match_state:
                    state = match_state[0]
                    grouped_expression = term.replace(f'({state})', '') if len(
                        grouped_expression) == 0 else grouped_expression + f"+{term.replace(f'({state})', '')}"
            else:
                reduced_equations.append(term)
        if len(grouped_expression) > 0:
            reduced_equations.append(
                f"({state_match})({grouped_expression})")

        return '||'.join(reduced_equations)

    def __count_states_in_expression(self, expression: str):
        match_state = list(
            set(re.findall(r'\((Q\d+)\)', expression)))
        return (match_state, len(match_state))

    def convert_to_regular_expression(self) -> str:
        equations: Dict[str, str] = {
            state: self.__simplify_equation(self.__arden_theorem(state, self.__get_equation_for_state(state))) for state in self.states}
        regexpList = {}
        while len(regexpList) != len(self.accept_states):
            for state in self.states:
                regexp_state = equations[state]
                (match_state, state_count) = self.__count_states_in_expression(
                    regexp_state)
                it = 0
                while state_count > 1 and it < 3:
                    it += 1
                    for match in match_state:
                        (_, subs_s_count) = self.__count_states_in_expression(
                            equations[match])
                        if match != state and subs_s_count <= 1:
                            subs_eq = equations[match].replace('||', '|')
                            regexp_state = regexp_state.replace(
                                f'({match})', f"({subs_eq})")
                            regexp_state = self.__reduce_equation_for_state(
                                regexp_state.split('||'), match)
                    regexp_state = self.__simplify_equation(self.__arden_theorem(
                        state, self.__simplify_equation(regexp_state)))
                    (match_state, state_count) = self.__count_states_in_expression(
                        regexp_state)
                    equations[state] = regexp_state
                    if state_count <= 1:
                        break
                if state_count <= 1 and len(match_state) > 0:
                    match = match_state[0]
                    (_, subs_s_count) = self.__count_states_in_expression(
                        equations[match])
                    if match != state and subs_s_count <= 1:
                        subs_eq = equations[match].replace('||', '|')
                        regexp_state = regexp_state.replace(
                            f'({match})', f"({subs_eq})")
                        regexp_state = self.__reduce_equation_for_state(
                            regexp_state.split('||'), match)
                        regexp_state = self.__simplify_equation(self.__arden_theorem(
                            state, regexp_state))
                        equations[state] = regexp_state
                if 'Q' not in regexp_state and state in self.accept_states:
                    regexpList[state] = regexp_state.replace('||', '+')
        return '+'.join(regexpList.values())

    def __check_state_in_exp(self, exp) -> bool:
        return 'Q' in exp and exp in self.states

    def __simplify_equation(self, expression: str) -> str:
        states_found: List[str] = []
        closures: Dict = {}
        symbol_expr: Dict = {}
        while '(' in expression:
            start = expression.rfind('(')
            end = expression.find(')', start)
            substring = expression[start+1:end]
            char_test = expression[end+1:end+2]
            if '||' not in substring:
                if '+' in substring:
                    symb_index = f"S{len(symbol_expr)}"
                    symbol_expr[symb_index] = f"({substring})"
                    expression = expression.replace(
                        f"({substring})", f"[{symb_index}]")
                else:
                    if char_test != '*':
                        if self.__check_state_in_exp(substring):
                            states_found.append(substring)
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
        while '[' in expression:
            for s in states_found:
                expression = expression.replace(f"[{s}]", f"({s})")
            for close, closured in closures.items():
                expression = expression.replace(f"[{close}]", f"({closured})")
            for sym_ind, sym_exp in symbol_expr.items():
                expression = expression.replace(f"[{sym_ind}]", f"{sym_exp}")
        return expression

    def __get_transition_state_symbol(self, transition: FrozenSet[str]) -> Tuple[str, str]:
        input_state = transition_symbol = ''
        for item in transition:
            if 'Q' in item:
                input_state = item
            else:
                transition_symbol = item
        return (input_state, transition_symbol)

    def __get_equation_for_state(self, state) -> str:
        equations: List[str] = []
        for transition, next_state in self.transitions.items():
            if next_state == state:
                (input_state, transition_symbol) = self.__get_transition_state_symbol(
                    transition)
                equations.append(f"({input_state}){transition_symbol}")
        if state == self.start_state:
            equations.append('ε')
        return '||'.join(equations)

    # def __simulate_transition(self, current_state: str, symbol: str) -> str:
    #     transition_key = frozenset({current_state, symbol}) if frozenset(
    #         {current_state, symbol}) in self.transitions else frozenset({symbol, current_state})
    #     return self.transitions.get(transition_key)

    # def check_string_input(self, string: str):
    #     if len(string) > 0:
    #         self.__check_string_symbol(string)
    #         current_state = self.start_state
    #         for idx, char in enumerate(string):
    #             next_state = self.__simulate_transition(current_state, char)

    #             print(
    #                 f"current_state: {current_state}, symbol: {char}[pos]:{idx} next_state: {next_state}")
    #             current_state = next_state
    #         return current_state in self.accept_states
    #     else:
    #         return self.start_state in self.accept_states

    # def __check_string_symbol(self, string: str):
    #     for char in string:
    #         if char not in self.alphabet:
    #             raise Exception(
    #                 f"Invalid character {char} in string. {char} doesn't exist in input alphabets.")
