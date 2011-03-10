from errors import *
from parse import *

from nodes import *
from ifelse import *
from loop import *
from func import *
from trycatch import *

from stdlib import stdlib

import weakref

class WordObject(object):
	pass

StringObject = str
NumberObject = int
StackObject = list

class IdentObject(WordObject):
	idents = weakref.WeakValueDictionary()
	def __init__(self, name):
		self.name = name
		self.idents[name] = self
	def __str__(self):
		return "'" + self.name + "'"
	def __repr__(self):
		return self.__str__()

class FuncObject(WordObject):
	def __init__(self, node):
		self.func_node = node

class Closure(WordObject):
	def __init__(self, env, parent, node):
		self.env = env
		self.parent = parent
		self.node = node
		self.words = {}

	def getword(self, ident):
		if ident in self.words:
			return self.words[ident]
		elif self.parent:
			return self.parent.getword(ident)
		else:
			return self.env.getword(ident)

	def setlocal(self, ident, value):
		self.words[ident] = value

	def setword(self, ident, value):
		if ident in self.words:
			self.words[ident] = value
		elif self.parent:
			self.parent.setword(ident, value)
		else:
			self.env.setword(ident, value)

	def __str__(self):
		if hasattr(self.node, 'name'):
			return 'Func ' + self.node.name
		else:
			return 'Labda'

class Environment(object):
	types = {NumberObject: 'num', StringObject: 'str', Closure: 'func',
			IdentObject: 'ident', StackObject: 'stack'}

	def __init__(self):
		self.words = stdlib
		self.stack = []
		self.call_stack = []

		self.step_eval(parse_line("set '(' '('"))
		self.step_eval(parse_line("set ')' ')'"))
		self.step_eval(parse_line("set ']' ']'"))

	def gettype(self, word):
		if type(word) not in self.types:
			return 'func' # assume implementation function
		#	raise DejaError() #wrong type, should not happen
		return self.types[type(word)]

	def ensure(self, word, *expected_types):
		if self.gettype(word) not in expected_types:
			raise DejaTypeError(self, word, len(expected_types) > 1 and ('one of ' + ', '.join(expected_types) or expected_types[0])
		return word

	def getword(self, word):
		if word in self.words:
			return self.words[word]
		else:
			raise DejaNameError(self, word)

	@staticmethod
	def getident(name):
		if name not in IdentObject.idents:
			return IdentObject(name)
		else:
			return IdentObject.idents[name]

	def setword(self, ident, value):
		self.words[ident] = value

	def pushvalue(self, value):
		self.stack.append(value)

	def pushword(self, word, closure):
		if isinstance(word, Closure):
			for name in word.node.arguments.children:
				word.setlocal(name.value, self.popvalue())
			return word.body, word
		elif callable(word):
			return word(self, closure)
		else:
			self.stack.append(word)

	def popvalue(self):
		if self.stack:
			return self.stack.pop()
		else:
			raise DejaStackEmpty(self)

	def makeword(self, word, closure):
		if isinstance(word, (Number, String)):
			return word.value
		elif isinstance(word, Ident):
			return self.getident(word.value)
		elif isinstance(word, ProperWord):
			return closure.getword(word.value)

	def getnextnode(self, node, closure):
		if node.children:
			return node.children[0]
		return self.getnextupnode(node, closure)

	def getnextupnode(self, node, closure):
		while node.parent:
			p = node.parent
			if isinstance(node, ForStatement):
				item = self.popvalue()
				hidden = self.popvalue()
				func = self.ensure(self.popvalue(), 'ident', 'func')
				p_ = 
				if func:
					p.info = (func, hidden)
					p.repeat = True
					p.closure.setlocal(p.countername, item)
					return p.body
				elif hidden:
					p.repeat = False
					p.closure.setlocal(p.countername, item)
					return p.body
			elif isinstance(node, ConditionClause):
				if isinstance(p, (WhileStatement, IfClause, ElseIfClause)):
					if self.popvalue():
						return p.body
				elif isinstance(p, ForStatement):
					item = self.popvalue()
					hidden = self.popvalue()
					func = self.ensure(self.popvalue(), 'ident', 'func')
					if func:
						p.info = (func, hidden)
						p.repeat = True
						p.closure.setlocal(p.countername, item)
						return p.body
					elif hidden:
						p.repeat = False
						p.closure.setlocal(p.countername, item)
						return p.body
			elif isinstance(node, BodyClause):
				if isinstance(p, WhileStatement):
					return p.condition
				elif isinstance(p, ForStatement):
					if p.repeat:
						self.call_stack.append(p)
						self.pushvalue(p.hidden)
						if self.gettype(p.func) == 'ident':
							p.func = closure.getword(p.func)
						return self.pushword(p.func, closure)
				elif isinstance(p, (IfClause, ElseIfClause)):
					node = p.parent
					continue
				elif isinstance(p, LabdaStatement):
					return self.call_stack.pop()
			i = p.children.index(node)
			if i < len(p.children) - 1:
				return p.children[i + 1]
			node = p

	def traceup(self, node): #look for an error handler
		while node:
			if isinstance(node, CatchStatement):
				return node.errorhandler
			node = node.parent

	def step_eval(self, node, closure = None):
		while node:
			if not closure or isinstance(node, (File, Statement)):
				closure = Closure(self, closure, node)

			if isinstance(node, Word):
				n = self.pushword(self.makeword(node, closure), closure)
				if n:
					self.call_stack.append(node)
					node, closure = n
					continue

			elif isinstance(node, LocalFuncStatement) and closure.parent:
				closure.parent.setlocal(node.name, closure)
				node = self.getnextupnode(node, closure)
				if type(node) == tuple:
					node, closure = node
				continue

			elif isinstance(node, FuncStatement):
				self.setword(node.name, closure)
				node = self.getnextupnode(node, closure)
				if type(node) == tuple:
					node, closure = node
				continue

			elif isinstance(node, LabdaStatement):
				self.stack.append(closure)
				node = self.getnextupnode(node, closure)
				if type(node) == tuple:
					node, closure = node
				continue

			node = self.getnextnode(node, closure)
			if type(node) == tuple:
				node, closure = node

			if isinstance(node, BodyClause) and isinstance(node.parent, ForStatement):
				func, hidden = node.parent.info
				self.pushvalue(hidden)
				if self.gettype(func) == 'ident':
					func = closure.getword(func)
				n = self.pushword(func)
				if n:
					node, closure = n

def eval(node, env=None):
	if not env:
		env = Environment()
	try:
		env.step_eval(node)
	except ReturnException:
		pass
	except RuntimeError as e:
		print(e)
	except DejaError as e:
		print(e)
