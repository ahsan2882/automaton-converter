from dfa import DFA
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from nfa import NFA, eNFA
from regexpressions import RegExpression
import base64

app = Flask(__name__)
CORS(app, support_credentials=True)


@app.route('/api/input_nfa', methods=['POST'])
@cross_origin(supports_credentials=True)
def input_nfa():
    payload = request.get_json()
    transitions_payload = payload['transitions']
    transitions = {}
    input_is_eNFA = False
    for transition in transitions_payload:
        key = frozenset({transition['state'], transition['symbol']})
        if transition['symbol'] == 'ε':
            input_is_eNFA = True
        if key in transitions:
            transitions[key].append(transition['next_state'])
        else:
            transitions[key] = [transition['next_state']]
    if input_is_eNFA:
        epsilon_NFA = eNFA(
            states=payload['states'],
            alphabet=payload['alphabets'],
            transitions=transitions,
            start_state=payload['startState'],
            accept_states=payload['acceptStates'],
        )
        epsilon_path = epsilon_NFA.create_graph('enfa1')
        nfa = epsilon_NFA.convert_to_nfa()
        with open(epsilon_path, "rb") as image_file:
            enfa_img = base64.b64encode(image_file.read()).decode()
    else:
        nfa = NFA(
            states=payload['states'],
            alphabet=payload['alphabets'],
            transitions=transitions,
            start_state=payload['startState'],
            accept_states=payload['acceptStates'],
        )
    nfa_path = nfa.create_graph('nfa')

    dfa: DFA = nfa.convert_to_dfa()
    dfa_path = dfa.create_graph('equivalentDFA')
    try:

        with open(nfa_path, "rb") as image_file:
            nfa_img = base64.b64encode(image_file.read()).decode()
        with open(dfa_path, "rb") as image_file:
            dfa_img = base64.b64encode(image_file.read()).decode()

    except FileNotFoundError:
        return jsonify({"error": "Image file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    regexp = dfa.convert_to_regular_expression()
    response = {'result_dfa': dfa_img,
                'result_regexp': regexp, 'result_nfa': nfa_img}
    if input_is_eNFA:
        response['result_enfa'] = enfa_img
    return jsonify(response)


@app.route('/api/input_dfa', methods=['POST'])
@cross_origin(supports_credentials=True)
def input_dfa():
    payload = request.get_json()
    transitions_payload = payload['transitions']
    transitions = {}
    print(transitions_payload)

    for transition in transitions_payload:
        key = frozenset({str(transition['state']).replace(
            'q', 'Q'), transition['symbol']})
        if key not in transitions:
            transitions[key] = str(transition['next_state']).replace('q', 'Q')
    dfa = DFA(
        states=[state.replace('q', 'Q') for state in payload['states']],
        accept_states=[state.replace('q', 'Q')
                       for state in payload['acceptStates']],
        alphabet=payload['alphabets'],
        transitions=transitions,
        start_state=payload['startState'].replace('q', 'Q')
    )

    dfa_path = dfa.create_graph('dfa')
    try:
        with open(dfa_path, "rb") as image_file:
            dfa_img = base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        return jsonify({"error": "Image file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    regexp = dfa.convert_to_regular_expression()
    my_dict = {'result_dfa': dfa_img,
               'result_regexp': regexp}
    return jsonify(my_dict)


@app.route('/api/input_regexp', methods=['POST'])
@cross_origin(supports_credentials=True)
def input_regex():
    payload = request.get_json()
    print(payload)
    regex = RegExpression()
    epsilon_NFA = regex.convert_to_FA(payload['regexp'])
    epsilon_path = epsilon_NFA.create_graph('enfa1')
    nfa: NFA = epsilon_NFA.convert_to_nfa()
    nfa_path = nfa.create_graph('nfa')
    dfa: DFA = nfa.convert_to_dfa()
    dfa_path = dfa.create_graph('equivalentDFA')
    try:
        with open(epsilon_path, "rb") as image_file:
            enfa_img = base64.b64encode(image_file.read()).decode()
        with open(nfa_path, "rb") as image_file:
            nfa_img = base64.b64encode(image_file.read()).decode()
        with open(dfa_path, "rb") as image_file:
            dfa_img = base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        return jsonify({"error": "Image file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    regexp = dfa.convert_to_regular_expression()
    response = {'result_dfa': dfa_img,
                'result_regexp': regexp, 'result_nfa': nfa_img, 'result_enfa': enfa_img}
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
