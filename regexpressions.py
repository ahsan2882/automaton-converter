from pprint import pprint
import re
import os
from typing import Dict, List, Union


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

    def convert_to_tree(self, exp: str):
        def tree_to_json(node: Node):
            if node is None:
                return None
            if node.operand.isalpha():
                return {'value': node.operand}
            left_tree = tree_to_json(node.left)
            right_tree = tree_to_json(node.right)
            nnode = {"value": node.operand, "left": left_tree}
            if right_tree:
                nnode["right"] = right_tree
            return nnode

        stack = []
        root: Node = self.update_tree(stack, exp)
        pprint(tree_to_json(root))

    def update_tree(self, stack: Union[List[Node], str], exp: str) -> Node:
        def reduce_group(group: List[Node], reverse: bool = False):
            if reverse:
                group.reverse()
            while len(group) > 0:
                if len(group) == 1:
                    return group.pop()
                last = group.pop()
                if last.operand in ['.', '*'] or last.operand.isalpha():
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
                    elif group[-1].operand.isalpha():
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
            if char == '(':
                stack.append(char)
            elif char == ')':
                # pop all chars until stack has '('
                group: List[Node] = []
                while stack and stack[-1] != '(':
                    group.append(stack.pop())
                stack.pop()
                stack.append(reduce_group(group, reverse=True))
            elif char == '*':
                # kleene is applied to single group only, group may contain single alphabetic characters or operations between them
                left = stack.pop()
                node = Node('*')
                node.left = left if isinstance(left, Node) else Node(left)
                stack.append(node)
            elif char == '+':
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
            else:
                node = Node(char)
                stack.append(node)
        return reduce_group(stack)
