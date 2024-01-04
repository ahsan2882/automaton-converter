import re
import os


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

    # def __convert_to_tree(self, expression,sc,cc):
    #     tree = {}
    #     exp = expression.split('+')
    #     tree['choices'] = [ex for ex in exp]
    #     for choice in tree['choices']:

    def simplify_regexp(self, expression: str) -> str:
        simplified_closures = {}
        contain_closure = {}
        while '(' in expression:
            start = expression.rfind('(')
            end = expression.find(')', start)
            substring = expression[start+1:end]
            if ('*' in substring or '&' in substring):
                if '[C' not in substring:
                    sci = f'C{len(simplified_closures)}'
                    simplified_closures[sci] = substring
                    expression = expression.replace(
                        f"({substring})", f"[{sci}]")
                else:
                    cclo = f"S{len(contain_closure)}"
                    contain_closure[cclo] = substring
                    expression = expression.replace(
                        f"({substring})", f"[{cclo}]")
        tree = self.__convert_to_tree(
            expression, simplified_closures, contain_closure)

        # def check_rule_pattern(exp: str, rule):
        #     result = self.rules[rule]
        #     ex = exp.split('+')
        #     pass

        # def apply_rules(expr: str):
        #     for rule in self.rules:
        #         expr = check_rule_pattern(expr, rule)
        #     return expr

        # simplified = expression
        # while True:
        #     prev_simplified = simplified
        #     simplified = apply_rules(simplified)
        #     if simplified == prev_simplified:
        #         break

        # return simplified
        # output = apply_rules(expression, self.rules)
        # while output != expression:
        #     expression = output
        #     output = apply_rules(expression, self.rules)
        # return output

        # def recursive_simplify(expr):
        #     return expr
        # while True:
        #     simplified = recursive_simplify(expression)
        #     if simplified == expression:
        #         break
        #     expression = simplified
        # return expression


class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


def create_tree(regex):
    if len(regex) == 0:
        return None

    if regex[0] == '(':
        count = 0
        for i in range(len(regex)):
            if regex[i] == '(':
                count += 1
            elif regex[i] == ')':
                count -= 1
            if count == 0:
                if i == len(regex) - 1:
                    return create_tree(regex[1:i])
                else:
                    break

        operator_index = i + 1
        if operator_index < len(regex):
            operator = regex[operator_index]
            node = Node(operator)
            node.left = create_tree(regex[1:i])
            node.right = create_tree(regex[i + 2:-1])
            return node

    node = Node(regex[0])
    node.left = create_tree(regex[1:])
    return node


def print_tree(root, level=0):
    if root:
        print("  " * level + str(root.value))
        print_tree(root.left, level + 1)
        print_tree(root.right, level + 1)


regex = "(((((b+b)+ab)+($+a((a+a)+b)))b)(b(bb)+a*))((b(b*(ca)))*+($+cb)b)"
tree = create_tree(regex)
print_tree(tree)
