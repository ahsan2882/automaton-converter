from collections import deque
import json
from typing import Dict, FrozenSet, List, Set, Tuple, Union
from graphviz import Digraph

from flask import jsonify


class NFA:

    def __init__(
        self,
        states: List[str],
        alphabet: List[str],
        transitions: Dict[FrozenSet[str], List[str]],
        start_state: str,
        accept_states: List[str],
    ):
        self.states: List[str] = states
        self.alphabet: List[str] = alphabet
        self.transitions: Dict[FrozenSet[str], List[str]] = transitions
        self.start_state: str = start_state
        self.accept_states: List[str] = accept_states

    def convert_to_JSON(self) -> Dict[str, Union[str, List[str], Dict[FrozenSet[str], List[str]]]]:
        def get_transition_state_symbol(transition: FrozenSet[str]) -> Tuple[str, str, List[str]]:
            input_state = transition_symbol = ''
            for item in transition:
                if 'q' in item and len(item) > 1:
                    input_state = item
                else:
                    transition_symbol = item
            return (input_state, transition_symbol, self.transitions[transition])
        transitions: Dict[Tuple[str, str], str] = {}
        for transition in self.transitions:
            (state, symbol, next_states) = get_transition_state_symbol(transition)
            for next_state in next_states:
                key = (state, next_state)
                if key not in transitions:
                    transitions[key] = symbol
                else:
                    transitions[key] += f',{symbol}'

        return {'states': self.states, 'alphabets': self.alphabet, 'start_state': self.start_state, 'accept_states': self.accept_states, 'transitions': transitions}

    def move(self, states: FrozenSet[str], symbol: str) -> FrozenSet[str]:
        move_states: Set[str] = set()
        for state in states:
            move_states.update(self.transitions.get(
                frozenset({state, symbol}), []))
        return frozenset(move_states)

    def create_graph(self, name):
        nfa_json: Dict[str, Union[str, List[str]]] = self.convert_to_JSON()

        nfa_dot = Digraph(name, filename=f'{name}.gv', engine='dot')
        nfa_dot.attr('node', shape='doublecircle')
        for state in nfa_json['accept_states']:
            nfa_dot.node(state, state)
        nfa_dot.attr('node', shape='circle')
        nfa_dot.attr(rankdir='LR')
        for state in nfa_json['states']:
            if state not in nfa_json['accept_states']:
                nfa_dot.node(state, state)
        for transition, symbols in nfa_json['transitions'].items():
            (state, next_state) = transition
            nfa_dot.edge(state, next_state, label=symbols)

        nfa_dot.render(name, format='svg', cleanup=True)
        return f'{name}.svg'

    def convert_to_dfa(self):
        from dfa import DFA
        dfa_states: Dict[FrozenSet[str], str] = {}
        queue: deque[FrozenSet[str]] = deque()

        start_closure: FrozenSet[str] = frozenset({self.start_state})
        dfa_states[frozenset(start_closure)] = "Q0"
        queue.append(start_closure)

        dfa_transitions: Dict[FrozenSet[str], str] = {}
        while queue:
            current_states: FrozenSet[str] = queue.popleft()
            for symbol in self.alphabet:
                next_states = self.move(states=current_states, symbol=symbol)

                if next_states not in dfa_states:
                    dfa_states[(next_states)] = f"Q{len(dfa_states)}"
                    queue.append(next_states)

                dfa_transitions[
                    frozenset({dfa_states[frozenset(current_states)], symbol})
                ] = dfa_states[frozenset(next_states)]
        dfa_accept_states: List[str] = [
            dfa_states[frozenset(state)]
            for state in dfa_states
            if any(s in self.accept_states for s in state)
        ]

        return DFA(
            states=list(dfa_states.values()),
            states_map=dfa_states,
            alphabet=self.alphabet,
            transitions=dfa_transitions,
            start_state="Q0",
            accept_states=dfa_accept_states,
        )


class eNFA:
    def __init__(
        self,
        states: List[str],
        alphabet: List[str],
        transitions: Dict[FrozenSet[str], List[str]],
        start_state: str,
        accept_states: List[str],
    ) -> None:
        self.states: List[str] = states
        self.alphabet: List[str] = alphabet
        self.transitions: Dict[FrozenSet[str], List[str]] = transitions
        self.start_state: str = start_state
        self.accept_states: List[str] = accept_states
        self.epsilon = "ε"

    def epsilon_closure(self, state: str) -> FrozenSet[str]:
        closure: Set[str] = {state}
        stack: List[str] = [state]
        while stack:
            current_state = stack.pop()
            epsilon_transitions = self.transitions.get(
                frozenset({current_state, "ε"}), []
            )
            for next_state in epsilon_transitions:
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)

        return frozenset(closure)

    def convert_to_JSON(self) -> Dict[str, Union[str, List[str], Dict[FrozenSet[str], List[str]]]]:
        def get_transition_state_symbol(transition: FrozenSet[str]) -> Tuple[str, str, List[str]]:
            input_state = transition_symbol = ''
            for item in transition:
                if 'q' in item and len(item) > 1:
                    input_state = item
                else:
                    transition_symbol = item
            return (input_state, transition_symbol, self.transitions[transition])
        transitions: Dict[Tuple[str, str], str] = {}
        for transition in self.transitions:
            (state, symbol, next_states) = get_transition_state_symbol(transition)
            for next_state in next_states:
                key = (state, next_state)
                if key not in transitions:
                    transitions[key] = symbol
                else:
                    transitions[key] += f',{symbol}'

        return {'states': self.states, 'alphabets': [*self.alphabet, 'ε'], 'start_state': self.start_state, 'accept_states': self.accept_states, 'transitions': transitions}

    def create_graph(self, name: str):
        nfa_json: Dict[str, Union[str, List[str]]] = self.convert_to_JSON()

        nfa_dot = Digraph(name, filename=f'{name}.gv', engine='dot')
        nfa_dot.attr('node', shape='doublecircle')
        for state in nfa_json['accept_states']:
            nfa_dot.node(state, state)
        nfa_dot.attr('node', shape='circle')
        nfa_dot.attr(rankdir='LR')
        for state in nfa_json['states']:
            if state not in nfa_json['accept_states']:
                nfa_dot.node(state, state)
        for transition, symbols in nfa_json['transitions'].items():
            (state, next_state) = transition
            nfa_dot.edge(state, next_state, label=symbols)

        nfa_dot.render(name, format='svg', cleanup=True)
        return f'{name}.svg'

    def convert_to_nfa(self) -> NFA:
        new_transitions: Dict[FrozenSet[str], List] = {}

        for state in self.states:
            for symbol in self.alphabet:
                reachable_states = self.epsilon_closure(state=state)

                next_states: Set[str] = set()
                for s in reachable_states:
                    next_states.update(self.transitions.get(
                        frozenset({s, symbol}), []))
                next_states_closure: Set = set()
                for ns in next_states:
                    next_states_closure |= self.epsilon_closure(ns)
                new_transitions[frozenset({state, symbol})] = list(
                    next_states_closure)
        return NFA(
            states=self.states,
            alphabet=self.alphabet,
            transitions=new_transitions,
            start_state=self.start_state,
            accept_states=self.accept_states,
        )
