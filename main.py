from dfa import DFA
from nfa import NFA

nfa = NFA(
    states=["q0", "q1", "q2"],
    alphabet=["0", "1"],
    transitions={
        frozenset({"q0", "0"}): ["q0", "q1"],
        frozenset({"q0", "1"}): ["q0"],
        frozenset({"q1", "1"}): ["q2"],
    },
    start_state="q0",
    accept_states=["q2"],
)
print(nfa.transitions[frozenset({"q0", "0"})])

dfa: DFA = nfa.convert_to_dfa()

print("DFA States:", dfa.states)
print("DFA Transitions:", dfa.transitions)
print("DFA Start State:", dfa.start_state)
print("DFA Accept States:", dfa.accept_states)
