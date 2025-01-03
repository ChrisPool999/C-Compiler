#include <unordered_map>
#include <stack>
#include <list>
#include <string>
#include <stdint.h>
#include <iostream>
#include <vector>
 

// SYMBOL

// - used to describe things
// - diffrent kinds of symbol
// - many properties are shared, some are different 

  // KINDS
    // struct defintion
    // - CONST STATIC EXTERN DEFINED
    // - block
    // - line declared
    // - lines used
    // - parameter list
    // - Size (implement later, unsure how know)

    // struct instance
    // - CONST STATIC EXTERN DEFINED POINTER
    // - block
    // - line declared
    // - lines used
    // - parameter list
  
    // function
    // - CONST STATIC EXTERN DEFINED POINTER
    // - block
    // - line declared
    // - lines used
    // - parameter list
    // - TYPE + POINTER
    // - POINTER

    // variable
    // - CONST STATIC EXTERN DEFINED
    // - block
    // - line declared
    // - lines used
    // - size
    // - TYPE + POINTER









// NOTE2SELF: static function just means it can only be used in this file, even if exported 
static constexpr uint32_t flag(int bit) {
  return 1 << bit;
}

enum class Type {
  INT,
  CHAR,
  FLOAT,
  DOUBLE,
  VOID
};

// variable TYPE = pointer

// function return TYPE = pointer
// function = pointer 

// struct defintion != pointer
// struct instance =  pointer

// handle pointer dimension...

// function, struct definition, struct instance, variable
enum class Flags {
  POINTER = flag(0),
  CONST = flag(1),
  STATIC = flag(2),  
  EXTERN = flag(3), 
  DEFINED = flag(4) 
};
// FLAG SAFETY CHECKS:
//  - <= 1 storage specifier
//  - struct defintion shouldnt be pointer

// - would be nice to have pointer held with the type, since thats where it logically belonds
// - sooo many properties and just getters and setters...

// function
// - block 
// - address
// - lineDeclared
// - linesUsed
// 

class Symbol {
  uint32_t block; // functions not always global... think int (*foo)(int);
  uint32_t* address; // struct defintion doesnt need one
  uint32_t lineDeclared;
  std::list<uint32_t> linesUsed;
  uint32_t flags;

  uint32_t getBlock();
  uint32_t* getAddress();
  uint32_t getLineDeclared();
  std::list<uint32_t> getLinesUsed();
  Flags getFlags(char*); 

  void setAddress();
  void addLineUsed();
  void setFlags(uint32_t flags);    
};

class ParamList {
  std::vector<Flags> paramList;
  void setParamList();
  std::vector<Flags> getParamList();
};

class Variable {
  Symbol base;
  Type type;
  uint32_t size;
  uint32_t dimension;
  char* initValue;

  void getType();
  uint32_t getSize();
  uint32_t getDimension();
  char* getInitValue();
  void setType();
  void setSize();
  void setDimension();
  void setInitValue();
};

class Function {
  Symbol base;
  ParamList parameters;
  Type returnType;

  Type getType();
  void setType();
};

class Struct {
  Symbol base;
  ParamList parameters;
  uint32_t size;

  uint32_t getSize();
  void setSize();
};

class SymbolTable {
private:

  // first stack --> function stack      second stack --> variable shadowing 
  std::stack<std::unordered_map<std::string, std::stack<Symbol>>> table;
public:

  void addName(char* name, uint32_t block, uint32_t lineDeclared);
  void removeName(char* name);
  bool checkExists(char*);
  void functionCall();
  void functionEnd();
};

// get split this up into a variable, method, stack
// split up the properties

// -- goal, split into smaller classes, and combine them


  // struct - address, size, lineDeclared, linesUsed, paramList, 
  // function - address, lineDeclared, linesUsed, paramList, TYPE, KIND, KINDAttribute, DEFINED
  // variable - block, address, size, line declared, linesUsed, dimension, initValue, TYPE, KIND, KINDAttribute, defined