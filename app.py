from flask import Flask, jsonify
from dfa import DFA
from nfa import NFA, eNFA
from regexpressions import RegExpression
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, support_credentials=True)

app = Flask(__name__)

@app.route('/nfa_to_dfa', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_nfa():
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

    dfa: DFA = nfa.convert_to_dfa()
    states_map = {str(tuple(k)): v for k, v in dfa.states_map.items()}
    transitions = {str(tuple(k)): v for k, v in dfa.transitions.items()}
    my_dict = {
        "states": dfa.states,
        "state_maps": states_map,
        "transitions": transitions,
        "start_state": dfa.start_state,
        "accept_states": dfa.accept_states
    }
    return jsonify(my_dict)  # assuming NFA has a to_dict method

if __name__ == '__main__':
    app.run(debug=True)