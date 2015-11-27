"""
The evaluation module contains all classes used to evaluate expressions.
"""
from printing import Printer
from expressions import Function, Sequence, Symbol, Bindings


class Kernel:
    """
    This class is provides the context for the evaluation of expressions. It manages the rule set, substitution
    environments and the the assigned attributes.
    """
    def __init__(self, printer=None):
        if printer is None:
            printer = Printer()
        self.printer = printer
        self.rules = []

    def add_rule(self, rule):
        """
        Add a rule to the kernel rule set.

        **Parameters:**

            *rule* - The rule to add.

        **Returns:**

            ``None``
        """
        self.rules.append(rule)

    def print(self, expression):
        """
        Prints the expression using the registered printer.

        **Parameters:**

            *expression* - The expression to print.

        **Returns:**

            ``None``
        """
        print(self.printer.to_string(expression))

    def evaluate(self, expression):
        """
        Evaluate the expression using the kernel rules set. Evaluation works by repeatedly applying all rules until the
        output no longer changes.
        Since rewriting system are turing complete it is impossible to know whether this will lead to an infinite loop.
        So the system keeps track of the number of replacements that have been made and when this number exceeds some
        threshold the kernel stops the evaluation and returns the expression it got.

        **Parameters:**

            *expression* - The expression to evaluate.

        **Returns:**

            The evaluated expression.
        """
        # FIXME: Somehow this function doesn't really do what it should. It calls itself more often than needed.
        changed = True
        old_expression = expression

        while changed:
            changed = False
            for rule in self.rules:
                c, expression = rule.apply(expression)
                changed = changed or c
                if changed:
                    # print(rule)
                    print(old_expression, '->', expression)
                    # print()
                    break

        # FIXME: This code is very slow. There has to be a better way!
        if isinstance(expression, Function):
            new_head = expression.head
            new_head = self.evaluate(new_head)
            new_arguments = []
            for argument in expression.argument_sequence.expressions:
                new_arguments.append(self.evaluate(argument))
            expression = Function(new_head, Sequence(new_arguments))

        if old_expression != expression:
            return self.evaluate(expression)
        return expression

    def evaluate_and_print(self, expression):
        """
        First evaluates the expression and then prints the evaluated expression using the registered printer.

        **Parameters:**

            *expression* - The expression to evaluate and print.

        **Returns:**

            ``None``
        """
        self.print(self.evaluate(expression))

kernel = Kernel()


class Rule:
    """
    Base class for all rules.
    """

    def apply(self, expression):
        """
        Applies this rule to the given expression. This method should be overwritten by anyone subclassing this class.

        **Parameters:**

            *expression* - The expression the rule is applied to.

        **Returns:**

            ``None``
        """
        pass


class SubstitutionRule(Rule):
    """
    A SubstitutionRule consists of a pattern, a substitution expression and zero or more guards. When applied it will
    check whether the given expression matches its pattern and substitute the matching expressions by the substitution
    expression.
    """

    def __init__(self, pattern, substitution, guards=None):
        if guards is None:
            guards = []
        self.guards = guards
        self.pattern = pattern
        self.substitution = substitution
        self.guards = guards

    def apply(self, expression):
        bindings = Bindings()
        for match in self.pattern.match(expression, bindings):
            bindings = match.bindings
            for guard in self.guards:
                if not kernel.evaluate(guard.substitute(bindings)) == Symbol('True'):
                    return False, expression
            return True, self.substitution.substitute(bindings)
        return False, expression

    def __str__(self):
        return str(self.pattern) + ' -> ' + str(self.substitution)


class LambdaRule(Rule):
    """
    A LambdaRule consists of a pattern, a lambda function and zero or more guards. When applied it will
    check whether the given expression matches its pattern and call the lambda function on the matching expressions.

    This rule is often used for addition and multiplication of integers which is hard to expression only using
    :py:class:`~evaluation.SubstitutionRule`.
    """

    def __init__(self, pattern, code, guards=None):
        if guards is None:
            guards = []
        self.guards = guards
        self.pattern = pattern
        self.code = code

    def apply(self, expression):
        bindings = Bindings()
        for match in self.pattern.match(expression, bindings):
            bindings = match.bindings
            guards_satisfied = True
            for guard in self.guards:
                if not kernel.evaluate(guard.substitute(bindings)) == Symbol('True'):
                    guards_satisfied = False
            if guards_satisfied:
                return True, self.code(bindings).substitute(bindings)
        return False, expression
