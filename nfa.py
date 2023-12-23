from collections import deque
from typing import Dict, FrozenSet, List, Set
from dfa import DFA


class NFA:
    def __init__(
        self,
        states: List[str],
        alphabet: List[str],
        transitions: Dict[FrozenSet[str], List[str]],
        start_state: str,
        accept_states: List,
    ) -> None:
        self.states: List[str] = states
        self.alphabet: List[str] = alphabet
        self.transitions: Dict[FrozenSet[str], List[str]] = transitions
        self.start_state: str = start_state
        self.accept_states: List = accept_states

    def move(self, states, symbol) -> FrozenSet:
        move_states = set()
        for state in states:
            move_states.update(self.transitions.get(frozenset({state, symbol}), []))

        return frozenset(move_states)

    def epsilon_closure(self, states: FrozenSet) -> FrozenSet:
        # Method to find epsilon closure, but since there are no epsilon transitions, it returns the input states
        return states

    def convert_to_dfa(self) -> DFA:
        dfa_states: Dict[FrozenSet, str] = {}
        queue = deque()

        start_closure: FrozenSet = self.epsilon_closure(states={self.start_state})
        dfa_states[frozenset(start_closure)] = "Q0"
        queue.append(start_closure)

        dfa_transitions: Dict[Set, Dict[FrozenSet, str]] = {}
        while queue:
            current_states: FrozenSet = queue.popleft()
            for symbol in self.alphabet:
                next_states: FrozenSet = self.epsilon_closure(
                    states=self.move(states=current_states, symbol=symbol)
                )

                if next_states not in dfa_states:
                    dfa_states[(next_states)] = f"Q{len(dfa_states)}"
                    queue.append(next_states)

                dfa_transitions[
                    (dfa_states[frozenset(current_states)], symbol)
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


class εNFA(NFA):
    def __init__(
        self, states, alphabet, transitions, start_state, accept_states
    ) -> None:
        super().__init__(
            states=states,
            alphabet=alphabet,
            transitions=transitions,
            start_state=start_state,
            accept_states=accept_states,
        )
        self.epsilon = "ε"

    def epsilon_closure(self, states):
        epsilon_closure_states = set(states)
        stack = list(states)
        while stack:
            state = stack.pop()
            for transition, next_states in self.transitions.items():
                if state in transition and self.epsilon in transition:
                    for next_state in next_states:
                        if next_state not in epsilon_closure_states:
                            epsilon_closure_states.add(next_state)
                            stack.append(next_state)

        # Add epsilon closure from the start state
        if self.start_state in epsilon_closure_states:
            for transition, next_states in self.transitions.items():
                if self.start_state in transition and self.epsilon in transition:
                    for next_state in next_states:
                        if next_state not in epsilon_closure_states:
                            epsilon_closure_states.add(next_state)
                            stack.append(next_state)

        return frozenset(epsilon_closure_states)

    def convert_to_nfa(self) -> NFA:
        transitions_without_epsilon = {}
        for state in self.states:
            for symbol in self.alphabet:
                epsilon_closure = self.epsilon_closure(self.move({state}, symbol))
                transitions_without_epsilon[frozenset({state, symbol})] = list(
                    epsilon_closure
                )
        return NFA(
            states=self.states,
            alphabet=self.alphabet,
            transitions=transitions_without_epsilon,
            start_state=self.start_state,
            accept_states=self.accept_states,
        )

    def convert_to_dfa(self) -> DFA:
        transitions_without_epsilon = {}
        for state in self.states:
            for symbol in self.alphabet:
                epsilon_closure = self.epsilon_closure(self.move({state}, symbol))
                transitions_without_epsilon[frozenset({state, symbol})] = list(
                    epsilon_closure
                )
        return super().convert_to_dfa()
