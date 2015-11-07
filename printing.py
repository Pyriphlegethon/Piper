"""
The printing module defines classes for turning :py:mod:`expressions` into strings. To define
your own printer subclass the :py:class:`~printing.Printer` class and overwrite the
:py:meth:`~printing.Printer.to_string` function.
The pre-defined printers are:

    * :py:class:`~printing.Printer`

    * :py:class:`~printing.PrettyPrinter`

    * :py:class:`~printing.LaTeXPrinter`

**Example:**

    The expression ``Integrate[Power[x, x], x]`` will be printed in three different ways:

        The ``Printer`` will yield ``Integrate[Power[x, x], x]``,

        the ``PrettyPrinter`` will yield ``Integrate[x ^ x, x]`` and

        the ``LaTeXPrinter`` will yield ``\int {x}^{x} \mathrm{d} x``.
"""
from collections import defaultdict
from expressions import Symbol, Function, Integer, Real, Complex, Rational
from copy import deepcopy

# FIXME: This whole module is utterly broken. Complete recode, especially the LaTeXPrinter.


class Printer:
    """
    Printer for turning expressions to strings. The expression will be turned into the full form string.
    """

    def to_string(self, expression):
        """
        Returns a string representation of the given expression. This will always return the full form. It will not
        replace common operators (e.g. ``Plus``, ``Times``, etc.). The returned string representation will be parsable
        by the parsing module.

        **Parameters:**

            *expression* - The expression to turn into a string.

        **Returns:**

            The string representation of the given expression.
        """

        return str(expression)


class PrettyPrinter(Printer):
    """
    Printer for turning expressions into a pretty printed string. Some operators (e.g. ``Plus``, ``Times``, etc.) will
    be replaced by their mathematical symbols.
    """

    def __init__(self):
        super().__init__()
        self.operator = {Symbol('Plus'): ' + ', Symbol('Times'): ' * ', Symbol('Power'): ' ^ '}

    def to_string(self, expression):
        """
        Returns a string representation of the given expression. This function replaces common operators (e.g. ``Plus``,
        ``Times``, etc.) by their corresponding mathematical symbol (e.g. ``+``, :math:`\\cdot`). The returned string
        representation will be parsable by the parsing module.

        **Parameters:**

            *expression* - The expression to turn into a string.

        **Returns:**

            The string representation of the given expression.
        """

        if isinstance(expression, Function):
            if expression.head in self.operator:
                return '(' + self.operator[expression.head].join(map(self.to_string, expression.argument_sequence.expressions)) + ')'
            return self.to_string(expression.head) + '[' + ', '.join(map(self.to_string, expression.argument_sequence.expressions)) + ']'
        elif isinstance(expression, Complex):
            if isinstance(expression.real, Integer) and expression.real.value == 0:
                return self.to_string(expression.imaginary) + 'i'
            return self.to_string(expression.real) + ' + ' + self.to_string(expression.imaginary) + 'i'
        elif isinstance(expression, Rational):
            return '(' + self.to_string(expression.numerator) + '/' + self.to_string(expression.denominator) + ')'
        else:
            return str(expression)


# FIXME: This is experimental code. Find a better way to generate LaTeX code.
class LaTeXPrinter(Printer):
    """
    Printer for turning expressions into LaTeX code.
    """

    def __init__(self):
        super().__init__()
        self.printer_dict = {Symbol('Integrate'): self._to_string_integrate, Symbol('Plus'): self._to_string_plus,
                             Symbol('Times'): self._to_string_times, Symbol('Power'): self._to_string_power,
                             Symbol('D'): self._to_string_d, Symbol('Symbol'): self._to_string_symbols,
                             Symbol('Integer'): self._to_string_integer, Symbol('Element'): self._to_string_element,
                             Symbol('Not'): self._to_string_not}
        self.precedence = defaultdict(int, {Symbol('Rational'): 3, Symbol('Real'): 4, Symbol('Complex'): 2,
                                            Symbol('Integer'): 4, Symbol('Symbol'): 4, Symbol('D'): 4,
                                            Symbol('Integrate'): 1, Symbol('Plus'): 2, Symbol('Times'): 3,
                                            Symbol('Power'): 3})

    def _negative(self, expression):
        if isinstance(expression, Function):
            return expression.head == Symbol('Times') and len(
                [argument for argument in expression.argument_sequence.expressions if self._negative(argument)]) % 2 == 1
        elif isinstance(expression, Real):
            return expression.value < 0.0
        elif isinstance(expression, Integer):
            return expression.value < 0
        else:
            return False

    def _as_non_negative(self, expression):
        if isinstance(expression, Integer):
            if self._negative(expression):
                return Integer(-1 * expression.value)
            else:
                return Integer(expression.value)
        elif isinstance(expression, Real):
            if self._negative(expression):
                return Real(-1.0 * expression.value)
            else:
                return Real(expression.value)
        elif isinstance(expression, Function):
            if expression.head == Symbol('Times'):
                argument_sequence.expressions = []
                for argument in expression.argument_sequence.expressions:
                    argument_sequence.expressions.append(self._as_non_negative(argument))
                return Function(Symbol('Times'), argument_sequence.expressions)
            else:
                return deepcopy(expression)
        else:
            return deepcopy(expression)

    def _to_string_integrate(self, expression):
        if isinstance(expression, Function) and expression.head == Symbol('Integrate') and len(
                expression.argument_sequence.expressions) == 2:
            return '\\int ' + self._to_string(expression.argument_sequence.expressions[0],
                                              self.precedence[expression.head]) + ' \\mathrm{d} ' + self._to_string(
                expression.argument_sequence.expressions[1], self.precedence[expression.head])
        elif isinstance(expression, Function) and expression.head == Symbol('Integrate') and len(
                expression.argument_sequence.expressions) == 4:
            return '\\int_{' + self._to_string(expression.argument_sequence.expressions[2],
                                               self.precedence[expression.head]) + '}^{' + self._to_string(
                expression.argument_sequence.expressions[3], self.precedence[expression.head]) + '} ' + self._to_string(
                expression.argument_sequence.expressions[0],
                self.precedence[
                    expression.head]) + ' \\mathrm{d} ' + self._to_string(
                expression.argument_sequence.expressions[1], self.precedence[expression.head])
        else:
            return self._to_string(expression.head) + '(' + ', '.join(map(self._to_string, expression.argument_sequence.expressions)) + ')'

    def _to_string_plus(self, expression):
        if isinstance(expression, Function) and expression.head == Symbol('Plus'):
            text = ''
            for argument in expression.argument_sequence.expressions:
                if not self._negative(argument):
                    text += self._to_string(argument, self.precedence[expression.head]) + ' + '
            text = text[:-3]
            for argument in expression.argument_sequence.expressions:
                if self._negative(argument):
                    text += ' - ' + self._to_string(self._as_non_negative(argument), self.precedence[expression.head])
            return text
        else:
            return self._to_string(expression.head) + '(' + ', '.join(map(self._to_string, expression.argument_sequence.expressions)) + ')'

    def _to_string_times(self, expression):
        if isinstance(expression, Function) and expression.head == Symbol('Times'):
            fraction = False
            for argument in expression.argument_sequence.expressions:
                if isinstance(argument, Function) and argument.head == Symbol('Power') and self._negative(argument.argument_sequence.expressions[1]):
                    fraction = True
            if fraction:
                text = '\\frac{'
                for argument in expression.argument_sequence.expressions:
                    if not (isinstance(argument, Function) and argument.head == Symbol('Power') and self._negative(argument.argument_sequence.expressions[1])):
                        text += self._to_string(argument, self.precedence[expression.head]) + ' \\cdot '
                text = text[:-7]
                text += '}{'
                for argument in expression.argument_sequence.expressions:
                    if isinstance(argument, Function) and argument.head == Symbol('Power') and self._negative(argument.argument_sequence.expressions[1]):
                        new_argument = deepcopy(argument)
                        new_argument.argument_sequence.expressions[1] = self._as_non_negative(new_argument.argument_sequence.expressions[1])
                        if isinstance(new_argument.argument_sequence.expressions[1], Integer) and new_argument.argument_sequence.expressions[1].value == 1:
                            new_argument = new_argument.argument_sequence.expressions[0]
                        text += self._to_string(new_argument, self.precedence[expression.head]) + ' \\cdot '
                text = text[:-7]
                return text + '}'
            else:
                text = ''
                for argument in expression.argument_sequence.expressions:
                    text += self._to_string(argument, self.precedence[expression.head]) + ' \\cdot '
                return text[:-7]
        else:
            return self._to_string(expression.head) + '(' + ', '.join(map(self._to_string, expression.argument_sequence.expressions)) + ')'

    def _to_string_power(self, expression):
        if isinstance(expression, Function) and expression.head == Symbol('Power') and len(expression.argument_sequence.expressions) == 2:
            if self._negative(expression.argument_sequence.expressions[1]):
                if isinstance(expression.argument_sequence.expressions[1], Integer) and expression.argument_sequence.expressions[1].value == 1:
                    return '\\frac{1}{' + self._to_string(expression.argument_sequence.expressions[0],
                                                          self.precedence[expression.head]) + '}'
                else:
                    return '\\frac{1}{{' + self._to_string(expression.argument_sequence.expressions[0],
                                                           self.precedence[expression.head]) + '}^{' + self._to_string(
                        self._as_non_negative(expression.argument_sequence.expressions[1]), self.precedence[expression.head]) + '}}'
            else:
                return '{' + self._to_string(expression.argument_sequence.expressions[0],
                                             self.precedence[expression.head]) + '}^{' + self._to_string(
                    expression.argument_sequence.expressions[1]) + '}'
        else:
            return self._to_string(expression.head) + '(' + ', '.join(map(self._to_string, expression.argument_sequence.expressions)) + ')'

    def _to_string_d(self, expression):
        if isinstance(expression, Function) and expression.head == Symbol('D') and len(expression.argument_sequence.expressions) == 2:
            return '\\partial_{' + self._to_string(expression.argument_sequence.expressions[1],
                                                   self.precedence[expression.head]) + '} ' + self._to_string(
                expression.argument_sequence.expressions[0], self.precedence[expression.head])
        else:
            return self._to_string(expression.head) + '(' + ', '.join(map(self._to_string, expression.argument_sequence.expressions)) + ')'

    @staticmethod
    def _to_string_symbols(expression):
        constants = {Symbol('Pi'): '\pi', Symbol('E'): 'e', Symbol('I'): 'i', Symbol('Sin'): '\\sin',
                     Symbol('Cos'): '\\cos', Symbol('Infinity'): '\\infty', Symbol('Alpha'): '\\alpha',
                     Symbol('Beta'): '\\beta', Symbol('Gamma'): '\\gamma'}
        if expression in constants:
            return constants[expression]
        else:
            return str(expression)

    def _to_string_integer(self, expression):
        if self._negative(expression):
            return '(' + str(expression) + ')'
        else:
            return str(expression)

    def _to_string_element(self, expression):
        if isinstance(expression, Function) and expression.head == Symbol('Element') and len(expression.argument_sequence.expressions) == 2:
            return self._to_string(expression.argument_sequence.expressions[0]) + ' \\in ' + self._to_string(expression.argument_sequence.expressions[1])
        else:
            return self._to_string(expression.head) + '(' + ', '.join(map(self._to_string, expression.argument_sequence.expressions)) + ')'

    def _to_string_not(self, expression):
        if isinstance(expression, Function) and expression.head == Symbol('Not') and len(expression.argument_sequence.expressions) == 1:
            return '\\neg ' + self._to_string(expression.argument_sequence.expressions[0])
        else:
            return self._to_string(expression.head) + '(' + ', '.join(map(self._to_string, expression.argument_sequence.expressions)) + ')'

    def _to_string(self, expression, precedence=-1):
        if expression.head in self.printer_dict:
            if self.precedence[expression.head] < precedence:
                return '(' + self.printer_dict[expression.head](expression) + ')'
            else:
                return self.printer_dict[expression.head](expression)
        elif isinstance(expression, Function):
            return self._to_string(expression.head) + '(' + ', '.join(map(self._to_string, expression.argument_sequence.expressions)) + ')'
        else:
            if self.precedence[expression.head] < precedence:
                return '(' + str(expression) + ')'
            else:
                return str(expression)

    def to_string(self, expression):
        """
        Returns a string representation of the given expression. The returned string will be in LaTeX format.

        **Warning:**

            The returned string will not be parsable by the parsing module.

        **Parameters:**

            *expression* - The expression to turn into a string.

        **Returns:**

            The LaTeX code for the given expression.
        """

        return self._to_string(expression)
