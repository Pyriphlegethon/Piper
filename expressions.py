"""
The classes in this module are used to represent mathematical expressions.
"""
from enum import Enum
from collections.abc import Iterator, Iterable
from itertools import permutations


class Pattern:
    def __init__(self, constant):
        self.constant = constant

    def match(self, expression, bindings):
        pass


class BoundPattern(Pattern):
    """
    A BoundPattern will match any expression that matches its base pattern. It then binds itself to matched expression.
    If it is matched a second time it will look if it is bound to the same expression it tries to match.
    """

    def __init__(self, name, base_pattern):
        super().__init__(False)
        self.name = name
        self.base_pattern = base_pattern

    def match(self, expression, bindings):
        if self.base_pattern.match(expression, bindings):
            if self.name in bindings:
                if bindings[self.name] == expression:
                    return SequenceMatchIterator([Match(bindings)])
                else:
                    return SequenceMatchIterator([])
            else:
                b = bindings
                b.bind(self.name, expression)
                return SequenceMatchIterator([Match(b)])
        else:
            return SequenceMatchIterator([])

    def __str__(self):
        return 'BoundPattern[' + self.name + ']'


class Blank(Pattern):
    """
    The Blank class will match any expression with the same head. If no head is passed in it will match any expression.
    """

    def __init__(self, head=None):
        super().__init__(False)
        self.head = head

    def match(self, expression, bindings):
        if self.head is None or self.head == expression.head:
            return SequenceMatchIterator([Match(bindings)])
        else:
            return SequenceMatchIterator([])

    def __str__(self):
        return 'Blank'


class Attribute(Enum):
    """
    Attributes define properties of expressions used in evaluation.
    """
    Orderless = 0
    """
    ``Orderless`` is an attribute assigned to functions to indicate that their arguments can be reordered arbitrarily.
    Usually the arguments will be sorted into a canonical form (similar to the way a human would sort them).
    ``Orderless`` corresponds to the mathematical notion of commutativity.

    **Example:**

        ``Plus[x, 2]`` will be sorted to yield ``Plus[2, x]``.

        ``Power[x, 2]`` however will not be reordered.
    """
    Flat = 1
    """
    ``Flat`` is an attribute assigned to functions to indicate that nested function calls can be flattened.
    ``Flat`` corresponds to the mathematical notion of associativity.

    **Example:**

        ``Plus[a, b, Plus[c, d]]`` will be flattened to yield ``Plus[a, b, c, d]``.

        ``Power[a, Power[b, c]]`` will not be flattened.
    """
    OneIdentity = 2
    """
    ``OneIdentity`` is an attribute assigned to functions to indicate that function calls with a single argument can be
    replaced by their argument.

    **Example:**

        ``Plus[x]`` will be replaced by ``x``.

        ``Sin[x]`` will not be replaced.
    """
    Numeric = 3
    """
    ``Numeric`` is an attribute assigned to symbols to indicate that they represent numerical values. Symbols that
    have some numerical value (even if it is unknown) behave quite differently from symbols that don't have a numerical
    value.

    **Example:**

        :math:`\pi` has the attribute ``Numeric``.

        :math:`\infty` doesn't have the attribute ``Numeric``.

        Therefore:

            :math:`\pi` - :math:`\pi` will yield ``0``.

            While :math:`\infty` - :math:`\infty` will not be evaluated.
    """
    Constant = 4
    """
    ``Constant`` is an attribute assigned to symbols to indicate that they are mathematical constants.
    This attribute is used in differentiation.

    **Example:**

        :math:`\pi` and :math:`e` have the attribute ``Constant`` while ``x`` doesn't.
    """
    NumericFunction = 5
    """
    ``NumericFunction`` is an attribute assigned to functions to indicate that they can be evaluated numerically given
    that all of their arguments can be evaluated numerically.

    **Example:**

        Given that the ``NumericFunction`` attribute wasn't assigned to the ``Cos`` function.

        ``Sin[3.0]`` will be evaluated numerically to yield ``-0.916522``.

        ``Cos[3.0]`` will not be evaluated.
    """
    Hold = 6
    """
    ``Hold`` is an attribute assigned to functions to indicate that their arguments should not be evaluated.

    **Example:**

        Given that ``f[x]`` has the attribute ``Hold`` and ``g[x]`` doesn't.

        ``f[Plus[2, 2]]`` will not be evaluated.

        ``g[Plus[2, 2]]`` will yield ``g[4]``.
    """
    Protected = 7
    """
    ``Protected`` is an attribute assigned to functions to indicate that they cannot be redefined.
    """


default_attributes = dict(Times=[Attribute.Flat, Attribute.Orderless, Attribute.OneIdentity],
                          Plus=[Attribute.Flat, Attribute.Orderless, Attribute.OneIdentity],
                          And=[Attribute.Flat, Attribute.Orderless, Attribute.OneIdentity],
                          Or=[Attribute.Flat, Attribute.Orderless, Attribute.OneIdentity],
                          Pi=[Attribute.Constant], E=[Attribute.Constant])


class Expression(Pattern):
    """
    Base class for all mathematical expressions. It consists of a head and a number of attributes. For a list of
    attributes see :py:class:`~evaluation.Attribute`.
    This is a base class and should not be instantiated. In some cases however it can be useful to subclass
    this class.
    """

    def __init__(self, head, attributes=None, constant=True):
        super().__init__(constant)
        self.head = head
        if attributes is None:
            self.attributes = []
        else:
            self.attributes = attributes

        if str(self.head) in default_attributes:
            self.attributes += default_attributes[str(self.head)]

    # FIXME: Attributes should really be stored in the kernel. Two different instances of Symbol with the same name
    # FIXME: should have the same attributes.
    def has_attribute(self, attribute):
        """
        Returns a boolean value indicating whether this expression has the given attribute.

        **Returns:**

            ``True`` if this expression has the given attribute. ``False`` otherwise.
        """
        return attribute in self.attributes

    def substitute(self, bindings):
        if str(self.head) in bindings:
            self.head = bindings[str(self.head)]
        return self

    def match(self, expression, bindings):
        return SequenceMatchIterator([Match(bindings)]) if self == expression else SequenceMatchIterator([])

    def __hash__(self):
        return hash(self.head)

    def __str__(self):
        return str(self.head)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return isinstance(other, Expression) and other.head == self.head


class Symbol(Expression):
    """
    Symbol class representing variables (e.g. ``x``), symbolic constants such as :math:`\\pi` and
    :math:`e` as well as other mathematical symbols like :math:`\infty`. Its head is the Symbol 'Symbol'.
    """

    def __init__(self, name, attributes=None):
        self.name = name
        if self.name in default_attributes:
            attributes = attributes + default_attributes[self.name] if attributes is not None else default_attributes[
                self.name]
        if name == 'Symbol':
            super().__init__(self, attributes)
        else:
            super().__init__(Symbol('Symbol'), attributes)

    def substitute(self, bindings):
        if self.name in bindings:
            return bindings[self.name]
        return self

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name


class Number(Expression):
    """
    Base class for every number expression.
    """

    def __init__(self, head, attributes=None):
        if attributes is None:
            attributes = [Attribute.Numeric, Attribute.Constant]
        else:
            attributes += [Attribute.Numeric]
        super().__init__(head, attributes)

    def __add__(self, other):
        pass

    def __sub__(self, other):
        return self.__add__(other * Integer(-1))

    def __mul__(self, other):
        pass

    def __truediv__(self, other):
        pass

    def __eq__(self, other):
        return isinstance(other, Number) and other.head == self.head


class Integer(Number):
    """
    Integer class representing an arbitrary sized integer. Its head is the Symbol 'Integer'.
    """

    def __init__(self, value):
        super().__init__(Symbol('Integer'))
        assert (isinstance(value, int))
        self.value = value

    def __add__(self, other):
        if isinstance(other, Integer):
            return Integer(self.value + other.value)
        if isinstance(other, Real):
            return Real(self.value + other.value)
        if isinstance(other, Rational):
            return other.__add__(Rational(self, Integer(1)))
        if isinstance(other, Complex):
            tmp = Complex(other.real + self, other.imaginary)
            if isinstance(tmp.imaginary, Integer) and tmp.imaginary.value == 0:
                return tmp.real
            return tmp

    def __mul__(self, other):
        if isinstance(other, Integer):
            return Integer(self.value * other.value)
        if isinstance(other, Real):
            return Real(self.value * other.value)
        if isinstance(other, Rational):
            return other.__mul__(Rational(self, Integer(1)))
        if isinstance(other, Complex):
            tmp = Complex(other.real * self, other.imaginary * self)
            if isinstance(tmp.imaginary, Integer) and tmp.imaginary.value == 0:
                return tmp.real
            return tmp

    def __truediv__(self, other):
        if isinstance(other, Integer):
            return Real(self.value / other.value)
        if isinstance(other, Real):
            return Real(self.value / other.value)
        if isinstance(other, Rational):
            tmp = Rational(self * other.denominator, other.numerator)
            if tmp.numerator.value == 0:
                return Integer(0)
            if tmp.denominator.value == 1:
                return tmp.numerator
            return tmp
        if isinstance(other, Complex):
            return Complex(self, Integer(0)).__truediv__(other)

    def __mod__(self, other):
        assert (isinstance(other, Integer))
        return Integer(self.value % other.value)

    def __hash__(self):
        return hash('Integer') + hash(self.value)

    def __eq__(self, other):
        return isinstance(other, Integer) and other.value == self.value

    def __str__(self):
        return str(self.value)


class Real(Number):
    """
    Real class representing a double precision floating point number. Its head is the Symbol 'Real'.
    """

    def __init__(self, value):
        super().__init__(Symbol('Real'))
        assert (isinstance(value, float))
        self.value = value

    def __add__(self, other):
        if isinstance(other, Integer):
            return Real(self.value + other.value)
        if isinstance(other, Real):
            return Real(self.value + other.value)
        if isinstance(other, Rational):
            return other.__add__(self)
        if isinstance(other, Complex):
            tmp = Complex(other.real + self, other.imaginary)
            if isinstance(tmp.imaginary, Integer) and tmp.imaginary.value == 0:
                return tmp.real
            return tmp

    def __mul__(self, other):
        if isinstance(other, Integer):
            return Real(self.value * other.value)
        if isinstance(other, Real):
            return Real(self.value * other.value)
        if isinstance(other, Rational):
            return other.__mul__(self)
        if isinstance(other, Complex):
            tmp = Complex(other.real * self, other.imaginary * self)
            if isinstance(tmp.imaginary, Integer) and tmp.imaginary.value == 0:
                return tmp.real
            return tmp

    def __truediv__(self, other):
        if isinstance(other, Integer):
            return Real(self.value / other.value)
        if isinstance(other, Real):
            return Real(self.value / other.value)
        if isinstance(other, Rational):
            return Real(self * other.denominator / other.numerator)
        if isinstance(other, Complex):
            return Complex(self, Integer(0)).__truediv__(other)

    def __str__(self):
        return str(self.value)

    def __hash__(self):
        return hash(self.head) + hash(self.value)

    def __eq__(self, other):
        return isinstance(other, Real) and other.value == self.value


class Rational(Number):
    """
    Rational class representing an arbitrary rational number. Its numerator and denominator are arbitrary integers.
    """

    def __init__(self, numerator, denominator):
        super().__init__(Symbol('Rational'))

        if isinstance(numerator, Integer) and isinstance(denominator, Integer) and denominator.value != 0:
            gcd = Rational.gcd(numerator, denominator)
            denominator = Integer(int(denominator.value / gcd.value))
            numerator = Integer(int(numerator.value / gcd.value))
            if denominator.value < 0 and numerator.value < 0:
                denominator = Integer(abs(denominator.value))
                numerator = Integer(abs(numerator.value))
            if denominator.value < 0 < numerator.value:
                denominator = Integer(abs(denominator.value))
                numerator = Integer(-1 * numerator.value)

        self.numerator = numerator
        self.denominator = denominator

    def match(self, expression, bindings):
        if not isinstance(expression, Rational):
            return SequenceMatchIterator([])

        numerator_match = self.numerator.match(expression.numerator, bindings)

        return SubMatchIterator(lambda m: self.denominator.match(expression.denominator,
                                                                 m.bindings), numerator_match)

    def __add__(self, other):
        if isinstance(other, Integer):
            return self.__add__(Rational(other, Integer(1)))
        if isinstance(other, Real):
            return self.numerator / self.denominator + other
        if isinstance(other, Rational):
            tmp = Rational(self.numerator * other.denominator + self.denominator * other.numerator,
                           self.denominator * other.denominator)
            if tmp.numerator.value == 0:
                return Integer(0)
            if tmp.denominator.value == 1:
                return tmp.numerator
            return tmp
        if isinstance(other, Complex):
            tmp = Complex(other.real + self, other.imaginary)
            if isinstance(tmp.imaginary, Integer) and tmp.imaginary.value == 0:
                return tmp.real
            return tmp

    def __mul__(self, other):
        if isinstance(other, Integer):
            return self.__mul__(Rational(other, Integer(1)))
        if isinstance(other, Real):
            return self.numerator / self.denominator * other
        if isinstance(other, Rational):
            tmp = Rational(self.numerator * other.numerator, self.denominator * other.denominator)
            if tmp.numerator.value == 0:
                return Integer(0)
            if tmp.denominator.value == 1:
                return tmp.numerator
            return tmp
        if isinstance(other, Complex):
            tmp = Complex(other.real * self, other.imaginary * self)
            if isinstance(tmp.imaginary, Integer) and tmp.imaginary.value == 0:
                return tmp.real
            return tmp

    def __truediv__(self, other):
        if isinstance(other, Integer):
            tmp = Rational(self.numerator, self.denominator * other)
            if tmp.numerator.value == 0:
                return Integer(0)
            if tmp.denominator.value == 1:
                return tmp.numerator
            return tmp
        if isinstance(other, Real):
            return Real((self.numerator / self.denominator) / other.value)
        if isinstance(other, Rational):
            return self * Rational(other.denominator, other.numerator)
        if isinstance(other, Complex):
            return Complex(self, Integer(0)).__truediv__(other)

    @staticmethod
    def gcd(a, b):
        """
        Calculates the greatest common divisor of two :py:class:`Integers<expressions.Integer>`.
        """
        x = Integer(abs(a.value))
        y = Integer(abs(b.value))

        if x.value == 0 and y.value == 0:
            return Integer(0)
        elif x.value == 0:
            return y
        elif y.value == 0:
            return x
        elif x.value % 2 == 0 and y.value % 2 == 0:
            return Integer(2 * Rational.gcd(Integer(x.value // 2), Integer(y.value // 2)).value)
        elif x.value % 2 == 0:
            return Rational.gcd(Integer(x.value // 2), y)
        elif y.value % 2 == 0:
            return Rational.gcd(x, Integer(y.value // 2))
        elif x.value >= y.value:
            return Rational.gcd(Integer((x.value - y.value) // 2), y)
        else:
            return Rational.gcd(Integer((y.value - x.value) // 2), x)

    @staticmethod
    def lcm(x, y):
        """
        Calculates the least common multiple of two :py:class:`Integers<expressions.Integer>`.
        """

        return (x * y) / Rational.gcd(x, y)

    def __str__(self):
        return "Rational[" + str(self.numerator) + ", " + str(self.denominator) + "]"

    def __eq__(self, other):
        return isinstance(other,
                          Rational) and other.numerator == self.numerator and other.denominator == self.denominator

    def __hash__(self):
        return hash(self.head) + hash(self.numerator) + hash(self.denominator)


class Complex(Number):
    """
    Complex class representing complex numbers. It consists of a real and an imaginary part.
    """

    def __init__(self, real, imaginary):
        super().__init__(Symbol('Complex'))
        assert (isinstance(real, Number) and isinstance(imaginary, Number))
        self.real = real
        self.imaginary = imaginary

        if isinstance(self.real, Complex):
            self.imaginary += self.real.imaginary
            self.real = self.real.real
        if isinstance(self.imaginary, Complex):
            self.real -= self.imaginary.imaginary
            self.imaginary = self.imaginary.real

    def match(self, expression, bindings):
        if not isinstance(expression, Complex):
            return SequenceMatchIterator([])

        real_match = self.real.match(expression.real, bindings)

        return SubMatchIterator(lambda m: self.imaginary.match(expression.argument_sequence,
                                                               m.bindings), real_match)

    def __add__(self, other):
        if isinstance(other, Complex):
            tmp = Complex(self.real + other.real, self.imaginary + other.imaginary)
            if isinstance(tmp.imaginary, Integer) and tmp.imaginary.value == 0:
                return tmp.real
            return tmp
        else:
            tmp = Complex(self.real + other, self.imaginary)
            if isinstance(tmp.imaginary, Integer) and tmp.imaginary.value == 0:
                return tmp.real
            return tmp

    def __mul__(self, other):
        if isinstance(other, Integer):
            tmp = Complex(self.real * other, self.imaginary * other)
            if isinstance(tmp.imaginary, Integer) and tmp.imaginary.value == 0:
                return tmp.real
            return tmp
        if isinstance(other, Real):
            tmp = Complex(self.real * other, self.imaginary * other)
            if isinstance(tmp.imaginary, Integer) and tmp.imaginary.value == 0:
                return tmp.real
            return tmp
        if isinstance(other, Rational):
            tmp = Complex(self.real * other, self.imaginary * other)
            if isinstance(tmp.imaginary, Integer) and tmp.imaginary.value == 0:
                return tmp.real
            return tmp
        if isinstance(other, Complex):
            tmp = Complex(self.real * other.real - self.imaginary * other.imaginary,
                          self.real * other.imaginary + self.imaginary * other.real)
            if isinstance(tmp.imaginary, Integer) and tmp.imaginary.value == 0:
                return tmp.real
            return tmp

    def __truediv__(self, other):
        if isinstance(other, Complex):
            div = other.real * other.real + other.imaginary * other.imaginary
            tmp = Complex(self.real * other.real + self.imaginary * other.imaginary,
                          self.imaginary * other.real - self.real * other.imaginary)
            if isinstance(tmp.real, Integer) and isinstance(div, Integer):
                tmp.real = Rational(tmp.real, div) * Integer(1)
            else:
                tmp.real = tmp.real / div
            if isinstance(tmp.imaginary, Integer) and isinstance(div, Integer):
                tmp.imaginary = Rational(tmp.imaginary, div) * Integer(1)
            else:
                tmp.imaginary = tmp.imaginary / div
            if isinstance(tmp.imaginary, Integer) and tmp.imaginary.value == 0:
                return tmp.real
            return tmp
        else:
            return self / Complex(other, Integer(0))

    def __str__(self):
        return "Complex[" + str(self.real) + ", " + str(self.imaginary) + "]"

    def __eq__(self, other):
        return isinstance(other, Complex) and other.real == self.real and other.imaginary == self.imaginary

    def __hash__(self):
        return hash(self.head) + hash(self.real) + hash(self.imaginary)


class Function(Expression):
    """
    Function class representing a composite expression consisting of a head and sequence of arguments the head is
    applied to. The attributes of the head will influence how this function is evaluated. If its head has the
    ``Orderless`` attribute this function will reorder its arguments into a canonical form:

        1. Integers
        2. Reals
        3. Symbols
        4. Functions

    If its head has the ``Flat`` attribute this function will flatten any nested function calls.
    For a complete list of attributes see :py:class:`~expressions.Attribute`.
    """

    def __init__(self, head, argument_sequence, attributes=None):
        if isinstance(head, str):
            head = Symbol(head)
        constant = head.constant and argument_sequence.constant
        if attributes is not None:
            super().__init__(head, [Attribute.Flat], constant)
        else:
            if isinstance(head, Pattern):
                super().__init__(head, [], constant)
            else:
                super().__init__(head, head.attributes, constant)

        if self.has_attribute(Attribute.Flat):
            argument_sequence = argument_sequence.flatten(self.head)

        if self.has_attribute(Attribute.Orderless):
            self.argument_sequence = argument_sequence.sort()
        else:
            self.argument_sequence = argument_sequence

        numeric = self.has_attribute(Attribute.NumericFunction) and self.argument_sequence.has_attribute(
            Attribute.Numeric)

        if numeric:
            self.attributes.append(Attribute.Numeric)

    def substitute(self, bindings):
        new_head = self.head.substitute(bindings)
        new_argument_sequence = self.argument_sequence.substitute(bindings)
        return Function(new_head, new_argument_sequence)

    def match(self, expression, bindings):
        if not isinstance(expression, Function):
            return SequenceMatchIterator([])
        head_match = self.head.match(expression.head, bindings)
        orderless = self.has_attribute(Attribute.Orderless)
        flat = self.has_attribute(Attribute.Flat)
        return SubMatchIterator(lambda m: self.argument_sequence.match(expression.argument_sequence,
                                                                       m.bindings, orderless=orderless, flat=flat,
                                                                       head=self.head), head_match)

    def __getitem__(self, item):
        if item == 0:
            return self.head
        else:
            return self.argument_sequence[item - 1]

    def __str__(self):
        return str(self.head) + str(self.argument_sequence)

    def __hash__(self):
        return hash(self.head) + hash(self.argument_sequence)

    def __eq__(self, other):
        return isinstance(other,
                          Function) and other.head == self.head and other.argument_sequence == self.argument_sequence


class Sequence(Expression):
    """
    Sequence class representing a sequence of expressions. This class is used for the arguments of a function.
    """

    def __init__(self, expressions):
        constant = all([expression.constant for expression in expressions])
        super().__init__(Symbol('Sequence'), constant=constant)
        self.expressions = expressions
        self.position = 0

    def flatten(self, head):
        new_expressions = []
        for argument in self.expressions:
            if isinstance(argument, Function) and argument.head == head:
                new_expressions += argument.argument_sequence.expressions
            else:
                new_expressions.append(argument)
        return Sequence(new_expressions)

    def sort(self, key=None):
        if key is None:
            key = str
        return Sequence(sorted(self.expressions, key=key))

    def substitute(self, bindings):
        new_expressions = []
        for argument in self.expressions:
            new_expressions.append(argument.substitute(bindings))
        return Sequence(new_expressions)

    def match(self, expression, bindings, orderless=False, flat=False, head=None):
        if orderless and flat:
            matcher = OrderlessFlatSequenceMatcher(expression.to_list(), self.to_list(), bindings, head)
        elif orderless:
            matcher = OrderlessSequenceMatcher(expression.to_list(), self.to_list(), bindings)
        elif flat:
            matcher = FlatSequenceMatcher(expression.to_list(), self.to_list(), bindings, head)
        else:
            matcher = SequenceMatcher(expression.to_list(), self.to_list(), bindings)
        return matcher.__iter__()

    def to_list(self):
        return [expression for expression in self]

    def __delitem__(self, key):
        del self.expressions[key]

    def __len__(self):
        return len(self.expressions)

    def __getitem__(self, item):
        return self.expressions[item]

    def __next__(self):
        if self.position < len(self):
            self.position += 1
            return self[self.position]
        raise StopIteration()

    def __hash__(self):
        h = 0
        for expression in self.expressions:
            h += hash(expression)
        return h

    def __str__(self):
        return "[" + ", ".join(map(str, self.expressions)) + "]"

    def __eq__(self, other):
        return isinstance(other, Sequence) and other.expressions == self.expressions


class Bindings:
    """
    The Bindings class keeps track of all the bindings in the matching process. Bindings are stored as a list of tuples
    (name, expression).
    """

    def __init__(self):
        self.bindings = set([])
        self.position = 0

    def bind(self, name, expression):
        """
        Binds a expression to a name.

        **Parameters:**

            *name* - The name the expression is bound to.

            *expression* - The expression to bind.

        **Returns:**

            ``None``
        """
        self.bindings.add((name, expression))

    def remove(self, name):
        """
        Removes a binding.

        **Parameters:**

            *name* - The name of the binding to remove.

        **Returns**:

            ``None``

        **Raises:**

            *KeyError* if no binding with *name* as name exists.
        """
        self.bindings.remove((name, self[name]))

    def union(self, other):
        b = Bindings()
        for name, expression in other.bindings:
            b.bind(name, expression)
        for name, expression in self.bindings:
            b.bind(name, expression)
        return b

    def __getitem__(self, key):
        for name, expression in self.bindings:
            if name == key:
                return expression
        raise KeyError()

    def __contains__(self, key):
        for name, expression in self.bindings:
            if name == key:
                return True
        return False

    def keys(self):
        keys = []
        for binding in self.bindings:
            keys.append(binding[0])
        return keys

    def __str__(self):
        return "{" + ", ".join([str(name) + ' -> ' + str(expression) for name, expression in self.bindings]) + "}"

    def __repr__(self):
        return str(self)


class Match:
    """
    A single match consisting of the matched expression, the pattern and the bindings.
    """

    def __init__(self, bindings=None):
        if bindings is None:
            bindings = Bindings()
        self.bindings = bindings

    def __str__(self):
        return str(self.bindings)

    def __repr__(self):
        return str(self)


class MatchIterator(Iterator):
    """

    """

    pass


class SequenceMatchIterator(Iterator):
    """
    Iterator over many :py:class:`matches<matching.Match>`.
    """

    def __init__(self, matches):
        self.matches = matches
        self.position = 0

    def add_match(self, match):
        self.matches.append(match)

    def add_matches(self, iterator):
        for match in iterator:
            self.add_match(match)

    def __len__(self):
        return len(self.matches)

    def __next__(self):
        if self.position >= len(self):
            raise StopIteration()
        item = self.matches[self.position]
        self.position += 1
        return item


class SubMatchIterator(SequenceMatchIterator):
    """

    """

    def __init__(self, closure, matches):
        super().__init__(matches)
        self._local = SequenceMatchIterator([])
        self.closure = closure

    def __next__(self):
        while True:
            try:
                local = self._local.__next__()
                return local
            except StopIteration:
                pass
            match = self.closure(self.matches.__next__())
            self._local = match


class SequenceMatcher(Iterable):
    """
    The SequenceMatcher class will try to match a list of patterns and expressions and return all matches as an
    iterator.
    """

    def __init__(self, expressions, patterns, bindings):
        super().__init__()
        self.expressions = expressions
        self.patterns = patterns
        self.bindings = bindings

    def _match(self, position=0, bindings=None):
        if len(self.patterns) != len(self.expressions):
            return SequenceMatchIterator([])

        if bindings is None:
            bindings = Bindings()
        bindings = bindings.union(self.bindings)
        if position >= len(self.patterns):
            return SequenceMatchIterator([Match(bindings)])

        match = self.patterns[position].match(self.expressions[position], bindings)

        return SubMatchIterator(lambda m: self._match(position + 1, bindings.union(m.bindings)), match)

    def __iter__(self):
        """
        Returns an iterator of all possible matches.

        **Returns**:

            ``An iterator over all possible matches.``
        """
        return self._match()


class MatchHelper:
    """

    """

    @staticmethod
    def _remove_element_that_matches(expressions, pattern):
        number = -1
        for i, element in enumerate(expressions):
            if pattern.match(element, Bindings()):
                number = i
                break
        if number != -1:
            del expressions[number]
            return True
        return False

    @staticmethod
    def eliminate_constants(expressions, patterns):
        constant_patterns = []
        for pattern in patterns:
            if pattern.constant:
                constant_patterns.append(pattern)

        for constant_pattern in constant_patterns:
            if not MatchHelper._remove_element_that_matches(expressions, constant_pattern):
                return False, None, None

        return True, expressions, [pattern for pattern in patterns if pattern not in constant_patterns]

    @staticmethod
    # FIXME: Found the culprit! What the heck is wrong with this code? I hope that this code is in fact incorrect and
    # FIXME: doesn't only show the bug.
    def eliminate_bound_patterns(expressions, patterns, bindings):
        return MatchHelper.eliminate_constants(expressions, patterns)


class OrderlessSequenceMatcher(Iterable):
    """
    The OrderlessSequenceMatcher class will try to match a list of patterns and a list of expressions and return all matches as
    an iterator. The lists can be reordered arbitrarily.
    """

    def __init__(self, expressions, patterns, bindings):
        super().__init__()
        self.expressions = expressions
        self.patterns = patterns
        self.bindings = bindings

    def _match(self):
        if len(self.expressions) != len(self.patterns):
            return SequenceMatchIterator([])

        if len(self.patterns) == 0:
            return SequenceMatchIterator(Match(self.bindings))

        worked, expressions, patterns = MatchHelper.eliminate_bound_patterns(self.expressions, self.patterns,
                                                                             self.bindings)

        if not worked:
            return SequenceMatchIterator([])

        return OrderlessMatchIterator(expressions, patterns, self.bindings)

    def __iter__(self):
        return self._match()


class OrderlessMatchIterator(Iterator):
    """

    """

    def __init__(self, expressions, patterns, bindings):
        super().__init__()
        self.expression_orderings = permutations(expressions)
        self.patterns = patterns
        self.bindings = bindings
        self._local = SequenceMatchIterator([])

    def __next__(self):
        while True:
            try:
                local = self._local.__next__()
                return local
            except StopIteration:
                pass

            ordering = list(self.expression_orderings.__next__())

            sm = SequenceMatcher(ordering, self.patterns, self.bindings)
            matches = sm.__iter__()
            self._local = matches


class GroupingIterator(Iterator):
    """

    """

    def __init__(self, elements, patterns, head):
        self.elements = elements
        self.number_of_groups = len(patterns)
        assert (self.number_of_groups > 1)
        self.marker_count = self.number_of_groups - 1
        self.markers = []
        self.endpoints = []
        self.exhausted = False
        self.current = None
        self.head = head
        self.patterns = patterns
        i = 0
        while i < self.marker_count:
            self.markers.append(i)
            self.endpoints.append(len(elements) - self.number_of_groups + i)
            i += 1

    def _advance(self):
        here = self.marker_count - 1

        while True:

            self.markers[here] += 1

            if self.markers[here] > self.endpoints[here]:
                here -= 1

                if here < 0:
                    self.exhausted = True
                    return
            else:
                i = here + 1
                while i < self.marker_count:
                    self.markers[i] = self.markers[i - 1] + 1
                    i += 1
                return

    def has_next(self):
        if self.exhausted:
            return False

        next_list = []
        for i in range(0, self.number_of_groups):
            next_list.append(0)

        marker = 0
        start_slice = 0

        while marker <= self.marker_count:
            end_slice = len(self.elements) if marker == self.marker_count else self.markers[marker]

            slice = self.elements[start_slice:end_slice + 1]

            next_list[marker] = slice

            start_slice += len(slice)
            marker += 1

        self.current = next_list
        self._advance()

        return True

    def __next__(self):
        if self.has_next():
            return self.current
        else:
            raise StopIteration


class FlatMatchIterator(Iterator):
    """

    """

    def __init__(self, expressions, patterns, bindings, head):
        super().__init__()
        self.expression_groupings = GroupingIterator(expressions, patterns, head)
        self.patterns = patterns
        self.bindings = bindings
        self._local = SequenceMatchIterator([])
        self.head = head

    def __next__(self):
        while True:
            try:
                local = self._local.__next__()
                return local
            except StopIteration:
                pass

            grouping = self.expression_groupings.__next__()

            new_expressions = [Function(self.head, Sequence(seq), [Attribute.Flat]) if len(seq) > 1 else seq[0] for seq in grouping if
                               len(seq) != 0]

            sm = SequenceMatcher(new_expressions, self.patterns, self.bindings)
            matches = sm.__iter__()
            self._local = matches


class FlatSequenceMatcher(Iterable):
    """
    The FlatSequenceMatcher class will try to match a list of patterns and list of expressions and return all matches as
    an iterator. The items in the lists can be grouped arbitrarily.
    """

    def __init__(self, expressions, patterns, bindings, head):
        super().__init__()
        self.expressions = expressions
        self.patterns = patterns
        self.bindings = bindings
        self.head = head

    def _match(self):
        if len(self.patterns) > len(self.expressions):
            return SequenceMatchIterator([])

        if len(self.patterns) == 0:
            if len(self.expressions) == 0:
                return SequenceMatchIterator([Match(self.bindings)])
            else:
                return SequenceMatchIterator([])

        if len(self.patterns) == len(self.expressions):
            return SequenceMatcher(self.expressions, self.patterns, self.bindings).__iter__()

        if len(self.patterns) == 1:
            return self.patterns[0].match(Function(self.head, Sequence(self.expressions), [Attribute.Flat]), self.bindings)

        return FlatMatchIterator(self.expressions, self.patterns, self.bindings, self.head)

    def __iter__(self):
        return self._match()


class OrderlessFlatIterator(Iterator):
    """

    """

    def __init__(self, expressions, patterns, bindings, head):
        super().__init__()
        self.expression_orderings = permutations(expressions)
        self.patterns = patterns
        self.bindings = bindings
        self._local = SequenceMatchIterator([])
        self.head = head

    def __next__(self):
        while True:
            try:
                local = self._local.__next__()
                return local
            except StopIteration:
                pass

            ordering = self.expression_orderings.__next__()

            fm = FlatSequenceMatcher(ordering, self.patterns, self.bindings, self.head)
            matches = fm.__iter__()
            self._local = matches


class OrderlessFlatSequenceMatcher(Iterable):
    """
    The OrderlessFlatSequenceMatcher class will try to match a list of patterns and list of expressions and return all
    matches as an iterator. The items in the lists can be grouped and reordered arbitrarily.
    """

    def __init__(self, expressions, patterns, bindings, head):
        super().__init__()
        self.expressions = expressions
        self.patterns = patterns
        self.bindings = bindings
        self.head = head

    def _match(self):
        if len(self.patterns) > len(self.expressions):
            return SequenceMatchIterator([])

        if len(self.patterns) == 0:
            if len(self.expressions) == 0:
                return SequenceMatchIterator([Match(self.bindings)])
            else:
                return SequenceMatchIterator([])
        else:
            if len(self.expressions) == 0:
                return SequenceMatchIterator([])

        if len(self.patterns) == len(self.expressions):
            return OrderlessSequenceMatcher(self.expressions, self.patterns, self.bindings).__iter__()

        worked, self.expressions, self.patterns = MatchHelper.eliminate_bound_patterns(self.expressions, self.patterns,
                                                                                       self.bindings)
        if not worked:
            return SequenceMatchIterator([])

        return OrderlessFlatIterator(self.expressions, self.patterns, self.bindings, self.head)

    def __iter__(self):
        return self._match()
