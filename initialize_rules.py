from expressions import Function, Symbol, Integer, Attribute, Sequence, BoundPattern, Blank, Complex, Number, Rational
from evaluation import SubstitutionRule, LambdaRule, kernel


kernel.add_rule(LambdaRule(Function(Symbol('ConstantQ'), Sequence([BoundPattern('a', Blank())])), lambda b: Symbol('True') if b['a'].has_attribute(Attribute.Constant) else Symbol('False')))
kernel.add_rule(LambdaRule(Function(Symbol('RealQ'), Sequence([BoundPattern('a', Blank())])), lambda b: Symbol('True') if isinstance(b['a'], Number) and not isinstance(b['a'], Complex) else Symbol('False')))
kernel.add_rule(SubstitutionRule(Function(Symbol('RealQ'), Sequence([Symbol('E')])), Symbol('True')))
kernel.add_rule(SubstitutionRule(Function(Symbol('RealQ'), Sequence([Symbol('Pi')])), Symbol('True')))
kernel.add_rule(LambdaRule(Function((Symbol('PositiveQ')), Sequence([BoundPattern('a', Blank(Symbol('Integer')))])), lambda b: Symbol('True') if b['a'].value > 0 else Symbol('False')))
kernel.add_rule(LambdaRule(Function(Symbol('NonNegativeQ'), Sequence([BoundPattern('a', Blank(Symbol('Integer')))])), lambda b: Symbol('True') if b['a'].value >= 0 else Symbol('False')))

kernel.add_rule(SubstitutionRule(Rational(BoundPattern('a', Blank()), Integer(1)), Symbol('a')))

kernel.add_rule(LambdaRule(Function(Symbol('Plus'), Sequence([BoundPattern('a', Blank(Symbol('Integer'))), BoundPattern('b', Blank(Symbol('Integer'))), BoundPattern('c', Blank())])), lambda b: Function('Plus', Sequence([b['a'] + b['b'], Symbol('c')]))))
kernel.add_rule(LambdaRule(Function(Symbol('Plus'), Sequence([BoundPattern('a', Blank(Symbol('Integer'))), BoundPattern('b', Blank(Symbol('Integer')))])), lambda b: b['a'] + b['b']))
kernel.add_rule(LambdaRule(Function(Symbol('Times'), Sequence([BoundPattern('a', Blank(Symbol('Integer'))), BoundPattern('b', Blank(Symbol('Integer')))])), lambda b: b['a'] * b['b']))
kernel.add_rule(LambdaRule(Function(Symbol('Power'), Sequence([BoundPattern('a', Blank(Symbol('Integer'))), BoundPattern('b', Blank(Symbol('Integer')))])), lambda b: Integer(b['a'].value ** b['b'].value), [Function(Symbol('NonNegativeQ'), Sequence([Symbol('b')]))]))

kernel.add_rule(SubstitutionRule(Function(Symbol('Plus'), Sequence([BoundPattern('a', Blank()), (Integer(0))])), Symbol('a')))

kernel.add_rule(SubstitutionRule(Function(Symbol('Plus'), Sequence([BoundPattern('a', Blank()), Function(Symbol('Times'), Sequence([BoundPattern('b', Blank()), BoundPattern('a', Blank())]))])), Function(Symbol('Times'), Sequence([Symbol('a'), Function('Plus', Sequence([Symbol('b'), Integer(1)]))]))))

kernel.add_rule(SubstitutionRule(Function(Symbol('Times'), Sequence([Blank(), Integer(0)])), Integer(0)))

kernel.add_rule(SubstitutionRule(Function(Symbol('Plus'), Sequence([BoundPattern('a', Blank()), BoundPattern('a', Blank()), BoundPattern('b', Blank())])), Function('Plus', Sequence([Symbol('b'), Function(Symbol('Times'), Sequence([Symbol('a'), Integer(2)]))]))))

kernel.add_rule(SubstitutionRule(Function(Symbol('Plus'), Sequence([BoundPattern('a', Blank()), BoundPattern('a', Blank())])), Function(Symbol('Times'), Sequence([Symbol('a'), Integer(2)]))))

kernel.add_rule(SubstitutionRule(Function((Symbol('Times')), Sequence([BoundPattern('a', Blank()), (Integer(1))])), Symbol('a')))

kernel.add_rule(SubstitutionRule(Function((Symbol('Times')), Sequence([BoundPattern('a', Blank()), BoundPattern('a', Blank())])), Function(Symbol('Power'), Sequence([Symbol('a'), Integer(2)]))))
kernel.add_rule(SubstitutionRule(Function((Symbol('Times')), Sequence([BoundPattern('b', Blank()), BoundPattern('a', Blank()), BoundPattern('a', Blank())])), Function('Times', Sequence([Function(Symbol('Power'), Sequence([Symbol('a'), Integer(2)])), Symbol('b')]))))

kernel.add_rule(SubstitutionRule(Function('Log', Sequence([Function('Power', Sequence([Symbol('E'), BoundPattern('a', Blank())]))])), Symbol('a'), [Function('RealQ', Sequence([Symbol('a')]))]))
kernel.add_rule(SubstitutionRule(Function('Log', Sequence([Integer(1)])), Integer(0)))
kernel.add_rule(SubstitutionRule(Function('Log', Sequence([BoundPattern('a', Blank()), BoundPattern('b', Blank())])), Function('Times', Sequence([Function('Log', Sequence([Symbol('b')])), Function('Power', Sequence([Function('Log', Sequence([Symbol('a')])), Integer(-1)]))]))))
kernel.add_rule(SubstitutionRule(Function('Log10', Sequence([BoundPattern('a', Blank())])), Function('Times', Sequence([Function('Log', Sequence([Symbol('a')])), Function('Power', Sequence([Function('Log', Sequence([Integer(10)])), Integer(-1)]))]))))
kernel.add_rule(SubstitutionRule(Function('Log2', Sequence([BoundPattern('a', Blank())])), Function('Times', Sequence([Function('Log', Sequence([Symbol('a')])), Function('Power', Sequence([Function('Log', Sequence([Integer(2)])), Integer(-1)]))]))))

kernel.add_rule(SubstitutionRule(Function('D', Sequence([Function('Power', Sequence([BoundPattern('a', Blank()), BoundPattern('b', Blank())])), BoundPattern('x', Blank(Symbol('Symbol')))])), Function('Times', Sequence([Function('Power', Sequence([Symbol('a'), Symbol('b')])), Function('Plus', Sequence([Function('Times', Sequence([Symbol('b'), Function('D', Sequence([Symbol('a'), Symbol('x')])), Function('Power', Sequence([Symbol('a'), Integer(-1)]))])), Function('Times', Sequence([Function('D', Sequence([Symbol('b'), Symbol('x')])), Function('Log', Sequence([Symbol('a')]))]))]))]))))
kernel.add_rule(SubstitutionRule(Function('D', Sequence([Function((Symbol('Times')), Sequence([BoundPattern('a', Blank()), BoundPattern('b', Blank())])), BoundPattern('x', Blank(Symbol('Symbol')))])), Function(Symbol('Plus'), Sequence([Function(Symbol('Times'), Sequence([Function(Symbol('D'), Sequence([Symbol('a'), Symbol('x')])), Symbol('b')])), Function(Symbol('Times'), Sequence([Function(Symbol('D'), Sequence([Symbol('b'), Symbol('x')])), Symbol('a')]))]))))
kernel.add_rule(SubstitutionRule(Function('D', Sequence([Function((Symbol('Plus')), Sequence([BoundPattern('a', Blank()), BoundPattern('b', Blank())])), BoundPattern('x', Blank(Symbol('Symbol')))])), Function(Symbol('Plus'), Sequence([Function(Symbol('D'), Sequence([Symbol('a'), Symbol('x')])), Function(Symbol('D'), Sequence([Symbol('b'), Symbol('x')]))]))))
kernel.add_rule(SubstitutionRule(Function('D', Sequence([BoundPattern('y', Blank()), BoundPattern('x', Blank(Symbol('Symbol')))])), Integer(0), [Function(Symbol('ConstantQ'), Sequence([Symbol('y')]))]))
kernel.add_rule(SubstitutionRule(Function('D', Sequence([BoundPattern('x', Blank()), BoundPattern('x', Blank(Symbol('Symbol')))])), Integer(1)))
kernel.add_rule(SubstitutionRule(Function('D', Sequence([BoundPattern('y', Blank(Symbol('Symbol'))), BoundPattern('x', Blank(Symbol('Symbol')))])), Integer(0)))
kernel.add_rule(SubstitutionRule(Function('D', Sequence([Function((Symbol('Cos')), Sequence([BoundPattern('y', Blank())])), BoundPattern('x', Blank(Symbol('Symbol')))])), Function(Symbol('Times'), Sequence([Integer(-1), Function(Symbol('Sin'), Sequence([Symbol('y')])), Function(Symbol('D'), Sequence([Symbol('y'), Symbol('x')]))]))))
kernel.add_rule(SubstitutionRule(Function('D', Sequence([Function((Symbol('Log')), Sequence([BoundPattern('y', Blank())])), BoundPattern('x', Blank(Symbol('Symbol')))])), Function(Symbol('Times'), Sequence([Function('Power', Sequence([Symbol('y'), Integer(-1)])), Function(Symbol('D'), Sequence([Symbol('y'), Symbol('x')]))]))))
kernel.add_rule(SubstitutionRule(Function('D', Sequence([Function(BoundPattern('f', Blank()), Sequence([BoundPattern('y', Blank())])), BoundPattern('x', Blank(Symbol('Symbol')))])), Function(Symbol('Times'), Sequence([Function(Function(Function('Derivative', Sequence([Integer(1)])), Sequence([Symbol('f')])), Sequence([Symbol('y')])), Function(Symbol('D'), Sequence([Symbol('y'), Symbol('x')]))]))))
kernel.add_rule(SubstitutionRule(Function(Function('Derivative', Sequence([Integer(1)])), Sequence([Symbol('Exp')])), Symbol('Exp')))
kernel.add_rule(SubstitutionRule(Function(Function('Derivative', Sequence([Integer(1)])), Sequence([Symbol('Sin')])), Symbol('Cos')))
kernel.add_rule(SubstitutionRule(Function(Function(Function('Derivative', Sequence([Integer(1)])), Sequence([Symbol('Cos')])), Sequence([BoundPattern('y', Blank())])), Function('Times', Sequence([Integer(-1), Function('Sin', Sequence([Symbol('y')]))]))))
kernel.add_rule(SubstitutionRule(Function(Function(Function('Derivative', Sequence([Integer(1)])), Sequence([Symbol('Log')])), Sequence([BoundPattern('y', Blank())])), Function('Power', Sequence([Symbol('y'), Integer(-1)]))))
kernel.add_rule(SubstitutionRule(Function(Function(Function('Derivative', Sequence([Integer(1)])), Sequence([Symbol('Log2')])), Sequence([BoundPattern('y', Blank())])), Function('Power', Sequence([Function('Times', Sequence([Function('Log', Sequence([Integer(2)])), Symbol('y')])), Integer(-1)]))))
kernel.add_rule(SubstitutionRule(Function(Function(Function('Derivative', Sequence([Integer(1)])), Sequence([Symbol('Log10')])), Sequence([BoundPattern('y', Blank())])), Function('Power', Sequence([Function('Times', Sequence([Function('Log', Sequence([Integer(10)])), Symbol('y')])), Integer(-1)]))))

kernel.add_rule(SubstitutionRule(Function(Symbol('Times'), Sequence([BoundPattern('a', Blank()), Function('Power', Sequence([BoundPattern('a', Blank()), BoundPattern('b', Blank(Symbol('Integer')))]))])), Function('Power', Sequence([Symbol('a'), Function('Plus', Sequence([Symbol('b'), Integer(1)]))]))))

kernel.add_rule(SubstitutionRule(Function(Symbol('Times'), Sequence([Function('Power', Sequence([BoundPattern('a', Blank()), BoundPattern('b', Blank())])), Function('Power', Sequence([BoundPattern('a', Blank()), BoundPattern('c', Blank())]))])), Function('Power', Sequence([Symbol('a'), Function('Plus', Sequence([Symbol('b'), Symbol('c')]))]))))

kernel.add_rule(SubstitutionRule(Function(Symbol('Times'), Sequence([BoundPattern('z', Blank()), BoundPattern('a', Blank()), Function('Power', Sequence([BoundPattern('a', Blank()), BoundPattern('b', Blank(Symbol('Integer')))]))])), Function('Times', Sequence([Function('Power', Sequence([Symbol('a'), Function('Plus', Sequence([Symbol('b'), Integer(1)]))])), Symbol('z')]))))

kernel.add_rule(SubstitutionRule(Function(Symbol('Times'), Sequence([BoundPattern('z', Blank()), Function('Power', Sequence([BoundPattern('a', Blank()), BoundPattern('b', Blank())])), Function('Power', Sequence([BoundPattern('a', Blank()), BoundPattern('c', Blank())]))])), Function('Times', Sequence([Function('Power', Sequence([Symbol('a'), Function('Plus', Sequence([Symbol('b'), Symbol('c')]))])), Symbol('z')]))))

kernel.add_rule(SubstitutionRule(Function('Power', Sequence([BoundPattern('a', Blank()), Integer(1)])), Symbol('a')))
kernel.add_rule(SubstitutionRule(Function('Power', Sequence([Blank(), Integer(0)])), Integer(1)))
kernel.add_rule(SubstitutionRule(Function('Power', Sequence([Integer(1), Blank()])), Integer(1)))
kernel.add_rule(SubstitutionRule(Function('Power', Sequence([Function(Symbol('Times'), Sequence([BoundPattern('a', Blank()), BoundPattern('b', Blank())])), BoundPattern('c', Blank(Symbol('Integer')))])), Function('Times', Sequence([Function('Power', Sequence([Symbol('a'), Symbol('c')])), Function('Power', Sequence([Symbol('b'), Symbol('c')]))]))))

kernel.add_rule(SubstitutionRule(Function('Power', Sequence([Function('Power', Sequence([BoundPattern('a', Blank()), BoundPattern('b', Blank())])), BoundPattern('c', Blank(Symbol('Integer')))])), Function('Power', Sequence([Symbol('a'), Function('Times', Sequence([Symbol('b'), Symbol('c')]))]))))

kernel.add_rule(SubstitutionRule(Function('And', Sequence([Symbol('True'), BoundPattern('a', Blank())])), Symbol('a')))
kernel.add_rule(SubstitutionRule(Function('And', Sequence([Symbol('False'), Blank()])), Symbol('False')))
kernel.add_rule(SubstitutionRule(Function('And', Sequence([BoundPattern('a', Blank()), Function('Not', Sequence([BoundPattern('a', Blank())]))])), Symbol('False')))
kernel.add_rule(SubstitutionRule(Function('And', Sequence([BoundPattern('a', Blank()), BoundPattern('a', Blank())])), Symbol('a')))

kernel.add_rule(SubstitutionRule(Function('Not', Sequence([Symbol('True')])), Symbol('False')))
kernel.add_rule(SubstitutionRule(Function('Not', Sequence([Symbol('False')])), Symbol('True')))
kernel.add_rule(SubstitutionRule(Function('Not', Sequence([Function('Not', Sequence([BoundPattern('a', Blank())]))])), Symbol('a')))

kernel.add_rule(SubstitutionRule(Function('Or', Sequence([Symbol('True'), BoundPattern('a', Blank())])), Symbol('True')))
kernel.add_rule(SubstitutionRule(Function('Or', Sequence([Symbol('False'), BoundPattern('a', Blank())])), Symbol('a')))
kernel.add_rule(SubstitutionRule(Function('Or', Sequence([BoundPattern('a', Blank()), Function('Not', Sequence([BoundPattern('a', Blank())]))])), Symbol('True')))
kernel.add_rule(SubstitutionRule(Function('Or', Sequence([BoundPattern('a', Blank()), BoundPattern('a', Blank())])), Symbol('a')))
kernel.add_rule(SubstitutionRule(Function('Or', Sequence([BoundPattern('a', Blank()), Function('And', Sequence([BoundPattern('a', Blank()), BoundPattern('b', Blank())])), BoundPattern('c', Blank())])), Function('Or', Sequence([Symbol('a'), Symbol('c')]))))
kernel.add_rule(SubstitutionRule(Function('Or', Sequence([BoundPattern('a', Blank()), Function('And', Sequence([Function('Not', Sequence([BoundPattern('a', Blank())])), BoundPattern('b', Blank())])), BoundPattern('c', Blank())])), Function('Or', Sequence([Symbol('a'), Symbol('b'), Symbol('c')]))))

kernel.add_rule(SubstitutionRule(Function('Implies', Sequence([BoundPattern('a', Blank()), BoundPattern('b', Blank())])), Function('Or', Sequence([Function('Not', Sequence([Symbol('a')])), Symbol('b')]))))
kernel.add_rule(SubstitutionRule(Function('Equivalent', Sequence([BoundPattern('a', Blank()), BoundPattern('b', Blank())])), Function('And', Sequence([Function('Implies', Sequence([Symbol('a'), Symbol('b')])), Function('Implies', Sequence([Symbol('b'), Symbol('a')]))]))))

kernel.add_rule(SubstitutionRule(Function('Log', Sequence([Symbol('E')])), Integer(1)))

kernel.add_rule(SubstitutionRule(Function('Exp', Sequence([BoundPattern('a', Blank())])), Function('Power', Sequence([Symbol('E'), Symbol('a')]))))

kernel.add_rule(SubstitutionRule(Function('Power', Sequence([Symbol('E'), Function('Log', Sequence([BoundPattern('a', Blank())]))])), Symbol('a')))

kernel.add_rule(SubstitutionRule(Function('Sin', Sequence([Function('Times', Sequence([Blank(Symbol('Integer')), Symbol('Pi')]))])), Integer(0)))
kernel.add_rule(SubstitutionRule(Function('Sin', Sequence([Symbol('Pi')])), Integer(0)))

kernel.add_rule(SubstitutionRule(Function('Sqrt', Sequence([BoundPattern('a', Blank())])),
                                 Function('Power', Sequence([Symbol('a'), Rational(Integer(1), Integer(2))]))))
