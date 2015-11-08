from expressions import Function, Symbol, Integer, Sequence
from time import clock
from initialize_rules import kernel


if __name__ == '__main__':
    exp = Function('D', Sequence([Function('Sin', Sequence([Function('Exp', Sequence([Function('Plus', Sequence([Integer(1), Symbol('a')]))]))])), Symbol('a')]))

    print(exp)
    start = clock()
    kernel.evaluate_and_print(exp)
    print(clock() - start)
