from typing import Dict, FrozenSet, List


class DFA:
    def __init__(
        self, states: List[str],
        states_map: Dict[FrozenSet[str], str],
        alphabet: List[str],
        transitions: Dict[FrozenSet[str], str],
        start_state: str,
        accept_states: List[str]
    ):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states
        self.states_map = states_map
