from collect import *

import struct

HEADER = '\x07DV\x04'
VERSION = (0, 0)
OP_SIZE = 5

OPCODES = {
	'PUSH_LITERAL':		'00000000',
	'PUSH_INTEGER':		'00000001',
	'PUSH_WORD':		'00000010',
	'SET':				'00000011',
	'SET_LOCAL':		'00000100',
	'SET_GLOBAL':		'00000101',
	'GET':				'00000110',
	'GET_GLOBAL':		'00000111',
	'JMP':				'00010000',
	'JMPZ':				'00010001',
	'RETURN':			'00010010',
	'LABDA':			'00100000',
	'ENTER_CLOSURE':	'00100001',
	'LEAVE_CLOSURE':	'00100010',
	'ADD':				'00110000',
	'SUB':				'00110001',
	'MUL':				'00110010',
	'DIV':				'00110011',
	'MOD':				'00110100',
	'DROP':				'01000000',
	'DUP':				'01000001',
	'NEW_STACK':		'01000010',
}
for k in OPCODES:
	OPCODES[k] = chr(int(OPCODES[k], 2))

TYPES = {
	'ident':	'00000000',
	'str':		'00000001',
	'num':		'00000010',
}
for k in TYPES:
	TYPES[k] = chr(int(TYPES[k], 2))

signed_int_s = struct.Struct('>i')
def signed_int(x):
	return signed_int_s.pack(x)

unsigned_int_s = struct.Struct('>I')
def unsigned_int(x):
	return unsigned_int_s.pack(x)

double_s = struct.Struck('>d')
def double(x):
	return double_s.pack(x)

def write_code(code, acc):
	for op in code:
		acc.append(OPCODES[op.opcode])
		acc.append(signed_int(op.ref))

def write_literals(literals, acc):
	for literal in literals:
		acc.append(TYPES[literal[0]])
		if literal[0] == 'num':
			acc.append(double(literal[1]))
		else
			acc.append(unsigned_int(literal[1]))
			acc.append(literal[1])

def write_bytecode(flat_code):
	code, literals = flat_code
	acc = [HEADER, chr(VERSION[0] * 16 + VERSION[1]), OP_SIZE * len(code)]
	write_code(code, acc)
	write_literals(literals, acc)
	return ''.join(acc)