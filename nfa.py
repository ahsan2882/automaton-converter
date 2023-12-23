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
            alphabet=self.alphabet,
            transitions=dfa_transitions,
            start_state="Q0",
            accept_states=dfa_accept_states,
        )
