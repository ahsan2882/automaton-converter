from typing import Dict, FrozenSet, List, Union


class Node:
    def __init__(self, operand):
        self.operand: str = operand
        self.left: Node = None
        self.right: Node = None


class RegExpression:
    def __init__(self):
        self.rules = {
            'ε*': 'ε',
            'εR': 'R',
            'Rε': 'R',
            'ε+R*': 'R*',
            'ε+RR*': 'R*',
            '(R+ε)*': 'R*',

            'R+R': 'R',
            'R*R*': 'R*',
            '(R*)*': 'R*',
            'RR*': 'R*R',
            'R*R': 'RR*',
            '(R)': 'R',
            'R+R*': 'R*',
            '(RR+R)*': 'R*',
            'R*RR*': 'RR*',

            '(R+P*)*': '(R+P)*',
            'PR+QR': '(P+Q)R',
            'RP+RQ': 'R(P+Q)',
            '(R+(Q+P))': 'R+Q+P',
            'PQ(RT)': 'PQRT',
            '(P*Q*)*': '(P*+Q*)*',
            '(P+Q)*': '(P*+Q*)*',
            # '(PQ)*P':'P(QP)*',
            # 'P(QP)*':'(PQ)*P',
            # '(P+Q)*':'(P*Q*)*',
            # '(P*Q*)*':'(P+Q)*',
            # '(P*+Q*)*':'(P+Q)*',
            # '(P*+Q*)*':'(P*Q*)*',
        }
        self.LEFT_PAREN = '('
        self.RIGHT_PAREN = ')'
        self.KLEENE = '*'
        self.CONCAT = '.'
        self.UNION = '+'

    def __convert_to_tree(self, exp: str) -> Node:
        stack: Union[List[Node], str] = []
        root: Node = self.__update_tree(stack, exp)
        return root

    def __update_tree(self, stack: Union[List[Node], str], exp: str) -> Node:
        def reduce_group(group: List[Node], reverse: bool = False):
            if reverse:
                group.reverse()
            while len(group) > 0:
                if len(group) == 1:
                    return group.pop()
                last = group.pop()
                if last.operand in ['.', '*'] or last.operand.isalnum():
                    if group[-1].operand == '+':
                        if group[-1].right is None:
                            llast = group.pop()
                            llast.right = last
                            group.append(llast)
                        else:
                            node = Node('.')
                            node.left = group.pop()
                            node.right = last
                            group.append(node)
                    elif group[-1].operand.isalnum() or group[-1].operand in ['*']:
                        node = Node('.')
                        node.left = group.pop()
                        node.right = last
                        group.append(node)
                elif last.operand == '+' and last.right is not None:
                    node = Node('.')
                    node.left = group.pop()
                    node.right = last
                    group.append(node)
            return group.pop()

        for char in exp:
            match char:
                case self.LEFT_PAREN:
                    stack.append(char)
                case self.RIGHT_PAREN:
                    # pop all chars until stack has '('
                    group: List[Node] = []
                    while stack and stack[-1] != '(':
                        group.append(stack.pop())
                    stack.pop()
                    stack.append(reduce_group(group, reverse=True))
                case self.KLEENE:
                    # kleene is applied to single group only, group may contain single alphabetic characters or operations between them
                    left = stack.pop()
                    node = Node('*')
                    node.left = left if isinstance(left, Node) else Node(left)
                    stack.append(node)
                case self.UNION:
                    group: List[Node] = []
                    while stack and stack[-1] != '(':
                        group.append(stack.pop())
                        if len(stack) == 0:
                            break
                    if len(group) > 1:
                        left_node = reduce_group(group, reverse=True)
                    else:
                        left_node = group.pop()
                    node = Node('+')
                    node.left = left_node if isinstance(
                        left_node, Node) else Node(left_node)
                    stack.append(node)
                case _:
                    stack.append(Node(char))
        return reduce_group(stack)

    def __build_FA_from_node(self, node: Node, states: List[str],
                             start_state: str, accept_states: List[str],
                             transitions: Dict[FrozenSet[str], List[str]],
                             alphabets: List[str], initial_state: str, final_state: str):
        def create_new_state():
            return f"q{len(states)}"

        if node.operand == self.UNION:
            # accept_states.append(new_state)
            (transitions, alphabets) = self.__build_FA_from_node(
                node.left, states, start_state, accept_states, transitions, alphabets, initial_state, final_state)
            (transitions, alphabets) = self.__build_FA_from_node(
                node.right, states, start_state, accept_states, transitions, alphabets, initial_state, final_state)
        elif node.operand == self.KLEENE:
            eps_state_1 = create_new_state()
            states.append(eps_state_1)
            key = frozenset({initial_state, 'ε'})
            if key in transitions:
                transitions[key].append(eps_state_1)
            else:
                transitions[key] = [eps_state_1]
            # eps_state_2 = create_new_state()
            key = frozenset({eps_state_1, 'ε'})
            if key in transitions:
                transitions[key].append(final_state)
            else:
                transitions[key] = [final_state]
            (transitions, alphabets) = self.__build_FA_from_node(
                node.left, states, start_state, accept_states, transitions, alphabets, eps_state_1, eps_state_1)
        elif node.operand == self.CONCAT:
            new_state = create_new_state()  # q2
            states.append(new_state)
            (transitions, alphabets) = self.__build_FA_from_node(
                node.left, states, start_state, accept_states, transitions, alphabets, initial_state, final_state=new_state)
            (transitions, alphabets) = self.__build_FA_from_node(node.right, states, start_state, accept_states,
                                                                 transitions, alphabets, initial_state=new_state, final_state=final_state)
        elif node.operand.isalnum():
            alphabets.append(node.operand)
            alphabets = list(set(alphabets))
            key = frozenset({initial_state, node.operand})
            if key in transitions:
                transitions[key].append(final_state)
            else:
                transitions[key] = [final_state]
        return (transitions, alphabets)

    def convert_to_FA(self, regexp: str):
        root: Node = self.__convert_to_tree(regexp)
        start_state = 'q0'
        accept_state: str = 'q1'
        states: List[str] = [start_state, accept_state]
        transitions: Dict[FrozenSet[str], List[str]] = {}
        alphabets: List[str] = []
        (transitions, alphabets) = self.__build_FA_from_node(
            root, states, start_state, accept_state, transitions, alphabets, start_state, final_state=accept_state)
        from nfa import eNFA
        return eNFA(states=states, alphabet=alphabets, transitions=transitions, start_state=start_state, accept_states=[accept_state])
