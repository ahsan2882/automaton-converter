import json
import pprint
from typing import Dict, List, Union
from graphviz import Digraph

from dfa import DFA
from nfa import NFA, eNFA
from regexpressions import RegExpression


regex = RegExpression()

nfa = NFA(
    states=["q0", "q1", "q2", "q3"],
    alphabet=["a", "b"],
    transitions={
        frozenset({"q0", "a"}): ["q1"],
        frozenset({"q0", "b"}): ["q2"],
        frozenset({"q1", "a"}): ["q3"],
        frozenset({"q1", "b"}): ["q0"],
        frozenset({"q2", "a"}): ["q0"],
        frozenset({"q2", "b"}): ["q3"],
        frozenset({"q3", "a"}): ["q3"],
        frozenset({"q3", "b"}): ["q3"],
    },
    start_state="q0",
    accept_states=["q0"],
)
nfa_json: Dict[str, Union[str, List[str]]] = nfa.convert_to_JSON()
nfa_dot = Digraph('NFA', filename='nfa.gv', engine='dot')
nfa_dot.attr('node', shape='doublecircle')
for state in nfa_json['accept_states']:
    nfa_dot.node(state, state)
nfa_dot.attr('node', shape='circle')
nfa_dot.attr(rankdir='LR')
for state in nfa_json['states']:
    if state not in nfa_json['accept_states']:
        nfa_dot.node(state, state)
for transition, symbols in nfa_json['transitions'].items():
    print(transition, symbols)
    (state, next_state) = transition
    nfa_dot.edge(state, next_state, label=symbols)

nfa_dot.render('nfa', format='svg', cleanup=True)
# nfa = NFA(
#     states=["q0", 'q1'],
#     alphabet=['a', 'b'],
#     transitions={
#         frozenset({"q0", "a"}): ["q1"],
#         frozenset({"q0", "b"}): ["q0"],
#         frozenset({"q1", "a"}): ["q1"],
#         frozenset({"q1", "b"}): ["q0"],
#     },
#     start_state='q0', accept_states=['q1']
# )
# nfa = NFA(
#     states=["q0", 'q1', 'q2'],
#     alphabet=['0', '1'],
#     transitions={
#         frozenset({"q0", "0"}): ["q0"],
#         frozenset({"q0", "1"}): ["q1"],
#         frozenset({"q1", "1"}): ["q1"],
#         frozenset({"q1", "0"}): ["q2"],
#         frozenset({"q2", "0"}): ["q2"],
#         frozenset({"q2", "1"}): ["q2"],
#     },
#     start_state='q0', accept_states=['q0', 'q1']
# )

# nfa = NFA(
#     states=["q0", 'q1', 'q2'],
#     alphabet=['a', 'b'],
#     transitions={
#         frozenset({"q0", "a"}): ["q0", "q1"],
#         frozenset({"q1", "a"}): ["q2"],
#         frozenset({"q1", "b"}): ["q0", "q1"],
#         frozenset({"q2", "b"}): ["q1"],
#     },
#     start_state='q0', accept_states=['q2']
# )

# dfa: DFA = nfa.convert_to_dfa()

# print("DFA States:", dfa.states)
# print("DFA Transitions:", dfa.transitions)
# print("DFA Start State:", dfa.start_state)
# print("DFA Accept States:", dfa.accept_states)
# print("DFA States Map:", dfa.states_map)
# # regexp = dfa.convert_to_regular_expression()
# # print(regexp)
# # breakpoint()
# epsi_nfa = regex.convert_to_FA('ab+((a+bc)*+(ba*c)*)c')

# nfa2 = epsi_nfa.convert_to_nfa()

# print("NFA 2 start state", nfa2.start_state)
# print("NFA 2 accept states", nfa2.accept_states)
# print("NFA 2 alphabet", nfa2.alphabet)
# print("NFA 2 states", nfa2.states)
# print("NFA 2 transitions", nfa2.transitions)

# dfa2 = nfa2.convert_to_dfa()
# print("DFA States:", dfa2.states)
# print("DFA Transitions:", dfa2.transitions)
# print("DFA Start State:", dfa2.start_state)
# print("DFA Accept States:", dfa2.accept_states)
# print("DFA States Map:", dfa2.states_map)
# breakpoint()
# min_dfa = dfa2.minimize_dfa(
#     states=dfa2.states, transitions=dfa2.transitions, accept_states=dfa2.accept_states)
# ((c+b)bcc)*
# c(d(cb)*+b)
# a(c+b)*+c
# c+(b+ab)*+a

# enfa = eNFA(
#     states=["q0", "q1", "q2"],
#     alphabet=["a", "b"],
#     transitions={
#         frozenset({"q0", "a"}): ["q0"],
#         frozenset({"q0", "b"}): ["q1"],
#         frozenset({"q0", "ε"}): ["q2"],
#         frozenset({"q1", "a"}): ["q0"],
#         frozenset({"q2", "b"}): ["q2"],
#     },
#     start_state="q0",
#     accept_states=["q2"],
# )

# nfa_from_enfa: NFA = enfa.convert_to_nfa()

# dfa2_from_eNFA: DFA = nfa_from_enfa.convert_to_dfa()
# print("NFA States:", nfa_from_enfa.states)
# print("NFA Transitions:", nfa_from_enfa.transitions)
# print("NFA Start State:", nfa_from_enfa.start_state)
# print("NFA Accept States:", nfa_from_enfa.accept_states)

# print("DFA 2 States:", dfa2_from_eNFA.states)
# print("DFA 2 Transitions:", dfa2_from_eNFA.transitions)
# print("DFA 2 Start State:", dfa2_from_eNFA.start_state)
# print("DFA 2 Accept States:", dfa2_from_eNFA.accept_states)
# print("DFA 2 States Map:", dfa2_from_eNFA.states_map)

# regexp = dfa2_from_eNFA.convert_to_regular_expression()
# print(regexp)

# input_string = 'abababababbb'
# print(dfa2_from_eNFA.check_string_input(input_string))

# dfa = DFA(
#     states=['Q0', 'Q1', 'Q2', 'Q3'],
#     accept_states=['Q1', 'Q3'],
#     alphabet=['a', 'b', 'c'],
#     transitions={
#         frozenset({'Q0', 'a'}): 'Q0',
#         frozenset({'Q0', 'b'}): 'Q0',
#         frozenset({'Q0', 'c'}): 'Q1',
#         frozenset({'Q1', 'a'}): 'Q2',
#         frozenset({'Q1', 'b'}): 'Q2',
#         frozenset({'Q1', 'c'}): 'Q0',
#         frozenset({'Q2', 'a'}): 'Q3',
#         frozenset({'Q2', 'b'}): 'Q2',
#         frozenset({'Q2', 'c'}): 'Q3',
#         frozenset({'Q3', 'a'}): 'Q0',
#         frozenset({'Q3', 'b'}): 'Q2',
#         frozenset({'Q3', 'c'}): 'Q1',
#     },
#     start_state='Q0'
# )
# breakpoint()
# regexpression = dfa.convert_to_regular_expression()
# print(regexpression)
# regex.simplify_regexp(regexpression)
