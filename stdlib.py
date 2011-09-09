from errors import *
from parse import *

stdlib = {}

def add(f, *names):
	if isinstance(f, str):
		return lambda x: add(x, f, *names)
	if not names:
		names = [f.__name__.rstrip('_').replace('_', '-')]
	for name in names:
		stdlib[name] = f
	return f

@add('.')
def prints(env, closure):
	print(env.popvalue())

@add
def swap(env, closure):
	a,b = env.popvalue(), env.popvalue()
	env.pushvalue(a)
	env.pushvalue(b)

@add('(print-stack)')
def print_stack(env, closure):
	print('[ ' + ' '.join(repr(x) for x in reversed(env.stack)) + ' ]')

@add
def dup(env, closure):
	if not env.stack:
		raise DejaStackEmpty(env)
	env.pushvalue(env.stack[-1])

@add
def drop(env, closure):
	env.popvalue()

@add
def get(env, closure):
	env.pushvalue(closure.getword(env.popvalue()))

@add
def getglobal(env, closure):
	env.pushvalue(env.getword(env.popvalue()))

@add
def set_(env, closure):
	ident = env.ensure(env.popvalue(), 'ident')
	value = env.popvalue()
	closure.setword(ident.name, value)

@add
def setglobal(env, closure):
	ident = env.ensure(env.popvalue(), 'ident')
	value = env.popvalue()
	env.setword(ident.name, value)

@add
def local(env, closure):
	ident = env.ensure(env.popvalue(), 'ident')
	value = env.popvalue()
	closure.setlocal(ident.name, value)

@add
def type_(env, closure):
	try:
		v = env.ensure(env.popvalue(), 'ident')
		env.pushvalue(env.getident(env.gettype(closure.getword(v.name))))
	except DejaNameError:
		env.pushvalue(env.getident('nil'))

@add('[]')
def newstack(env, closure):
	env.pushvalue([])

@add
def push_to(env, closure):
	stack = env.ensure(env.popvalue(), 'stack')
	stack.append(env.popvalue())

@add
def pop_from(env, closure):
	stack = env.popvalue()
	env.ensure(stack, 'stack')
	if not stack:
		raise DejaStackEmpty(env)
	env.pushvalue(stack.pop())

@add
def call(env, closure):
	p = env.popvalue()
	if env.gettype(p) == 'ident':
		p = closure.getword(p.name)
	env.pushword(p, closure)

@add('error', 'raise')
def error(env, closure):
	sort = env.popvalue()
	env.ensure(sort, 'ident')
	raise DejaError(env, sort.name, env.popvalue())

@add('=', 'equal')
def eq(env, closure):
	env.pushvalue(int(env.popvalue() == env.popvalue()))

@add('!=', 'not-equal')
def ne(env, closure):
	env.pushvalue(int(env.popvalue() != env.popvalue()))

@add('<', 'less')
def lt(env, closure):
	env.pushvalue(env.ensure(env.popvalue(), 'num') < env.ensure(env.popvalue(), 'num'))

@add('<=', 'less-or-equal')
def le(env, closure):
	env.pushvalue(env.ensure(env.popvalue(), 'num') <= env.ensure(env.popvalue(), 'num'))

@add('>', 'greater')
def gt(env, closure):
	env.pushvalue(env.ensure(env.popvalue(), 'num') > env.ensure(env.popvalue(), 'num'))

@add('>=', 'greater-or-equal')
def ge(env, closure):
	env.pushvalue(env.ensure(env.popvalue(), 'num') >= env.ensure(env.popvalue(), 'num'))

@add
def not_(env, closure):
	env.pushvalue(int(not env.popvalue()))

@add
def and_(env, closure):
	env.pushvalue(env.popvalue() and env.popvalue())

@add
def or_(env, closure):
	env.pushvalue(env.popvalue() or env.popvalue())

@add
def xor(env, closure):
	env.pushvalue(int(bool(env.popvalue()) != bool(env.popvalue())))

@add('+', 'add')
def plus(env, closure):
	env.pushvalue(env.ensure(env.popvalue(), 'num') + env.ensure(env.popvalue(), 'num'))

@add('-', 'sub')
def sub(env, closure):
	env.pushvalue(env.ensure(env.popvalue(), 'num') - env.ensure(env.popvalue(), 'num'))

@add('*', 'mul')
def mul(env, closure):
	env.pushvalue(env.ensure(env.popvalue(), 'num') * env.ensure(env.popvalue(), 'num'))

@add('/', 'div')
def div(env, closure):
	dividend = env.ensure(env.popvalue(), 'num')
	divisor = env.ensure(env.popvalue(), 'num')
	if not divisor:
		raise DejaDivisionByZero(env)
	env.pushvalue(int(dividend / divisor))

@add('%', 'mod')
def mod(env, closure):
	dividend = env.ensure(env.popvalue(), 'num')
	divisor = env.ensure(env.popvalue(), 'num')
	if not divisor:
		raise DejaDivisionByZero(env)
	env.pushvalue(int(dividend % divisor))

@add
def return_(env, closure):
	if self.call_stack:
		closure = self.call_stack.pop()
		return closure.node, closure
	else:
		raise ReturnException

@add('[')
def stackify(env, closure):
	v = env.popvalue()
	acc = []
	while env.gettype(v) != 'ident' or v.name != ']':
		acc.insert(0, v)
		v = env.popvalue()
	env.pushvalue(acc)

@add
def stop_iter(env, closure=False):
	env.pushvalue(0)
	env.pushvalue(closure is True)
	env.pushvalue(0)

@add
def range_(env, closure):
	curr = env.popvalue()
	step = 1
	if isinstance(curr, list):
		step, stop, curr = curr
	else:
		stop = env.popvalue()
		step = 1
	if (step > 0 and curr >= stop) or (step < 0 and curr <= stop):
		return stop_iter(env)
	env.pushvalue(env.getident('range'))
	env.pushvalue([step, stop, curr + step])
	env.pushvalue(curr)
	return closure.node, closure

@add
def in_(env, closure):
	stack = env.ensure(env.popvalue(), 'stack')
	if not stack:
		return stop_iter(env)
	env.pushvalue(env.getident('in'))
	env.pushvalue(stack)
	env.pushvalue(stack.pop())
	return closure.node.body, closure

@add
def reversed_(env, closure):
	env.pushvalue(list(reversed(env.ensure(env.popvalue(), 'stack'))))

@add('reversed!')
def reversed__(env, closure):
	stack = env.ensure(env.popvalue(), 'stack')
	stack.reverse()
	env.pushvalue(stack)

@add
def push_through(env, closure):
	stack = env.ensure(env.popvalue(), 'stack')
	stack.append(env.popvalue())
	env.pushvalue(stack)

@add
def copy_stack(env, closure):
	env.pushvalue(list(env.ensure(env.popvalue(), 'stack')))

@add
def catch_if(env, closure):
	i1 = env.ensure(env.popvalue(), 'ident')
	i2 = env.ensure(env.popvalue(), 'ident')
	stack = env.ensure(env.popvalue(), 'stack')
	if i1 != i2:
		raise DejaError(env, i2, stack)
	env.pushvalue(stack)
	env.pushvalue(i1)

used = set()

@add
def use(env, closure):
	fname = env.ensure(env.popvalue(), 'str')
	if fname not in used:
		try:
			tree = parse(fname)
		except IOError as e:
			raise DejaIOError(env, e.args[1], e.filename)
		used.add(fname)
		env.step_eval(tree)

@add('(ident-count)')
def ident_count(env, closure):
	print(len(env.getident('(').idents))

@add
def import_(env, closure):
	for key, value in __import__(env.ensure(env.popvalue(), 'str'), globals(), locals(), ['DEJA_VU']).DEJA_VU.iteritems():
		closure.setword(key, value)
