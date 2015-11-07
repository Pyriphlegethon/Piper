from expressions import Function, Symbol, Integer, Sequence, Real, Rational, Complex, BoundPattern, Blank, Bindings
from time import clock
from initialize_rules import kernel


if __name__ == '__main__':
    exp = Function('D', Sequence([Function('Plus', Sequence([Symbol('a'), Symbol('c'), Symbol('c'), Symbol('c'), Symbol('c')])), Symbol('a')]))

    print(exp)
    start = clock()
    kernel.evaluate_and_print(exp)
    print(clock() - start)
