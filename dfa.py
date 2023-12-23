class DFA:
    def __init__(
        self, states, states_map, alphabet, transitions, start_state, accept_states
    ):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states
        self.states_map = states_map
