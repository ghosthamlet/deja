#ifndef VALUE_DEF
#define VALUE_DEF

#include <stdbool.h>
#include <stdint.h>

#define isInt(x) ((long int)x & 1)
#define canBeInt(x) (x > INTPTR_MIN >> 1 && x < INTPTR_MAX >> 1)
#define toInt(x) ((long int)x>>1)
#define intToV(x) ((V)((x << 1) + 1))

#define toFile(x) ((File*)x->data.object)
#define toScope(x) ((Scope*)(x + 1))
#define toFunc(x) ((Func*)(x + 1))
#define toStack(x) ((Stack*)x->data.object)
#define toString(x) ((String*)(x + 1))
#define toCharArr(x) ((char*)(x + 1))
#define getChars(x) (toCharArr(toString(x)))
#define toNumber(x) (isInt(x) ? (double)toInt(x) : x->data.number)
#define toCFunc(x) (((ValueCFunc*)(x))->f)
#define toHashMap(x) ((HashMap*)(x + 1))
#define getType(x) (isInt(x) ? T_NUM : x->type)

#define new_dict() new_sized_dict(16)

// Déjà Vu utilises the synchronous cycle collection algorithm
// described by David F. Bacon and V.T. Rajan (2001)
typedef enum GCColor
{
	Black,	//In use or free
	Gray,	//Possible member of cycle
	White,	//Member of garbage cycle
	Purple,	//Possible root of cycle
	Green	//Acyclic
} GCColor;

typedef struct Value
{
	int type;
	GCColor color;
	bool buffered;
	unsigned int refs;
	union
	{
		double number;
		void* object;
	} data;
} Value;

typedef Value* V;

typedef struct String
{
	uint32_t length;
	uint32_t hash;
} String;

typedef struct
{
	Value v;
	String s;
} StrValue;

uint32_t string_hash(int, const char*);

V int_to_value(long int);
V double_to_value(double);
V a_to_value(char*);
V str_to_value(int, char*);
V empty_str_to_value(int, char**);
V get_ident(const char*);
V new_list();
V new_sized_dict();

bool truthy(V);

#endif
