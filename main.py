from dfa import DFA
from nfa import NFA, εNFA

# nfa = NFA(
#     states=["q0", "q1", "q2", "q3"],
#     alphabet=["a", "b", "c"],
#     transitions={
#         frozenset({"q0", "b"}): ["q2"],
#         frozenset({"q0", "c"}): ["q1"],
#         frozenset({"q1", "a"}): ["q3"],
#         frozenset({"q1", "b"}): ["q1", "q3"],
#         frozenset({"q2", "c"}): ["q2", "q3"],
#         frozenset({"q3", "c"}): ["q0"],
#     },
#     start_state="q0",
#     accept_states=["q0", "q3"],
# )
# print(nfa.transitions[frozenset({"q0", "b"})])

# dfa: DFA = nfa.convert_to_dfa()

# print("DFA States:", dfa.states)
# print("DFA Transitions:", dfa.transitions)
# print("DFA Start State:", dfa.start_state)
# print("DFA Accept States:", dfa.accept_states)
# print("DFA States:", dfa.states_map)


εnfa = εNFA(
    states=["q0", "q1", "q2", "q3", "q4"],
    alphabet=["0", "1"],
    transitions={
        frozenset({"q0", "1"}): ["q1"],
        frozenset({"q0", "ε"}): ["q2"],
        frozenset({"q1", "1"}): ["q0"],
        frozenset({"q2", "0"}): ["q3"],
        frozenset({"q2", "1"}): ["q4"],
        frozenset({"q3", "0"}): ["q2"],
        frozenset({"q4", "0"}): ["q2"],
    },
    start_state="q0",
    accept_states=["q2"],
)

nfa_from_εnfa: NFA = εnfa.convert_to_nfa()

# dfa1_from_εnfa: DFA = εnfa.convert_to_dfa()

# dfa2_from_εNFA: DFA = nfa_from_εnfa.convert_to_dfa()
print("NFA States:", nfa_from_εnfa.states)
print("NFA Transitions:", nfa_from_εnfa.transitions)
print("NFA Start State:", nfa_from_εnfa.start_state)
print("NFA Accept States:", nfa_from_εnfa.accept_states)

# print("DFA 1 States:", dfa1_from_εnfa.states)
# print("DFA 1 Transitions:", dfa1_from_εnfa.transitions)
# print("DFA 1 Start State:", dfa1_from_εnfa.start_state)
# print("DFA 1 Accept States:", dfa1_from_εnfa.accept_states)

# print("DFA 2 States:", dfa2_from_εNFA.states)
# print("DFA 2 Transitions:", dfa2_from_εNFA.transitions)
# print("DFA 2 Start State:", dfa2_from_εNFA.start_state)
# print("DFA 2 Accept States:", dfa2_from_εNFA.accept_states)
